from datetime import datetime
from urllib.parse import parse_qs, urlparse

import boto3
from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from moto import mock_aws

from app.tests.assertions import assert_contains_html
from app.tests.factories import FileFactory, FileMetadataFactory

db_date_format = "%Y-%m-%d"
python_date_format = "%d/%m/%Y"


def create_mock_s3_bucket_with_object(bucket_name, file):
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    file_object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )
    file_object.put(Body="record")
    return bucket


def expected_download_html_with_citeable_reference(
    jinja_env, file_id, file_name_download, file_name
):
    return jinja_env.from_string("""
        {% from 'govuk_frontend_jinja/components/button/macro.html' import govukButton %}
        <div class="rights-container">
            <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
            {{ govukButton({
                'text': 'Download record',
                'href': '/download/' ~ file_id,
                'classes': 'govuk-button__download--record',
                'attributes': {'aria-label': 'Download record ' ~ file_name}
            }) }}
            <p class="govuk-body govuk-body--download-filename">
                The downloaded record will be named<br>
                <strong>{{ file_name_download }}</strong>
            </p>
            <p class="govuk-body govuk-body--terms-of-use">
                Refer to <a href="/terms-of-use" class="govuk-link govuk-link--ayr">Terms of use.</a>
            </p>
        </div>
    """).render(
        file_id=file_id,
        file_name_download=file_name_download,
        file_name=file_name,
    )


def expected_download_html_without_citeable_reference(
    jinja_env, file_id, file_name
):
    return jinja_env.from_string("""
        {% from 'govuk_frontend_jinja/components/button/macro.html' import govukButton %}
        <div class="rights-container">
            <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
            {{ govukButton({
                'text': 'Download record',
                'href': '/download/' ~ file_id,
                'classes': 'govuk-button__download--record',
                'attributes': {'aria-label': 'Download record ' ~ file_name}
            }) }}
            <p class="govuk-body govuk-body--terms-of-use">
                Refer to <a href="/terms-of-use" class="govuk-link govuk-link--ayr">Terms of use.</a>
            </p>
        </div>
    """).render(file_id=file_id, file_name=file_name)


class TestRecord:
    @property
    def route_url(self):
        return "/record"

    @mock_aws
    def test_record_back_link_direct_navigation_goes_to_browse_records_without_query(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a user navigates directly to a record page
        When they inspect the back link
        Then it points to browse records with no sort or filters applied
        """
        file = FileFactory()
        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")
        back_link = soup.select_one("a.govuk-back-link")

        assert back_link is not None

        parsed_back_link = urlparse(back_link["href"])
        assert parsed_back_link.path == "/browse/records"
        assert parsed_back_link.query == ""

    def test_record_back_link_preserves_browse_records_filters_and_sort(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a user navigates to a record from browse records
        When they inspect the back link on the record page
        Then it keeps the previously selected browse sort and filters
        """
        mock_all_access_user(client)
        browse_query = (
            "transferring_body_filter=second_body"
            "&series_filter=second_series"
            "&sort=file_name-asc"
        )

        browse_response = client.get(f"/browse/records?{browse_query}")

        assert browse_response.status_code == 200

        browse_soup = BeautifulSoup(browse_response.data, "html.parser")
        record_link = browse_soup.select_one(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )

        assert record_link is not None

        record_href = record_link["href"]
        expected_query_params = parse_qs(browse_query, keep_blank_values=True)
        parsed_record_href = urlparse(record_href)

        assert (
            parse_qs(parsed_record_href.query, keep_blank_values=True)
            == expected_query_params
        )

        record_response = client.get(record_href)

        assert record_response.status_code == 200

        record_soup = BeautifulSoup(record_response.data, "html.parser")
        back_link = record_soup.select_one("a.govuk-back-link")

        assert back_link is not None

        parsed_back_link = urlparse(back_link["href"])
        assert parsed_back_link.path == "/browse/records"
        assert (
            parse_qs(parsed_back_link.query, keep_blank_values=True)
            == expected_query_params
        )

    def test_record_invalid_id_raises_404(self, client: FlaskClient):
        """
        Given a UUID, `invalid_file_id`, not corresponding to the id
        of a file in the database
        When a GET request is made to records page
        Then a 404 http response is returned
        """
        response = client.get("{self.route_url}/some-id")

        assert response.status_code == 404

    @mock_aws
    def test_record_top_search(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        And the HTML content should show top search component
        on the page
        """
        mock_all_access_user(client)

        file = FileFactory()

        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        label = soup.find("legend", {"class": "top-search__els__heading"})
        label_text = label.get_text(strip=True)
        textbox = soup.find("input", {"id": "search-input"})
        button = soup.find("button", {"id": "search-submit"})

        assert label is not None and label_text == "Search for digital records"
        assert textbox is not None
        assert button is not None

    @mock_aws
    def test_record_header_and_title(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        And the HTML content should show the header and title values
        """

        file = FileFactory()
        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        expected_header_title_html = f"""
                                <span class="record-page__scope-text">{file.consignment.series.body.Name}</span>
                                </p>
                                <h2 class="record-page__heading" id="record-heading" aria-live="polite">{file.FileName}</h2>
                """

        assert_contains_html(
            expected_header_title_html,
            html,
            "h2",
            {"id": "record-heading"},
        )

    @mock_aws
    def test_record_record_arrangement(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        And the HTML content should see record arrangement based on file path
        on the page
        """

        file = FileFactory(FilePath="data/content/test_folder/open_file.docx")
        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        record_path_details = file.FilePath.split("/")

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        expected_arrangement_html = f"""
        <div class="record-container">
            <h2 class="govuk-heading-m govuk-heading-m__record-header">Record arrangement</h2>
            <ol class="record-arrangement-list">
                <li class="govuk-body__record-arrangement-list">{record_path_details[0]}</li>
                <li class="govuk-body__record-arrangement-list">{record_path_details[1]}</li>
                <li class="govuk-body__record-arrangement-list">{record_path_details[2]}</li>
                <li class="govuk-body__record-arrangement-list">{record_path_details[3]}</li>
            </ol>
        </div>
        """

        assert_contains_html(
            expected_arrangement_html,
            html,
            "div",
            {"class": "record-container"},
        )

    @mock_aws
    def test_record_record_alert_banner_is_visible_when_unsupported_file_extension(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is not compatible with IIIF
        Then the alert banner responsible with alerting the user should be visible
        """

        file = FileFactory(ffid_metadata__Extension="docx")

        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        banner = soup.find("h2", string="Unable to display this record")
        assert banner is not None

    @mock_aws
    def test_record_record_alert_banner_is_visible_when_unsupported_file_extension_no_ffid_metadata(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File with no FFID metadata in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is not compatible with IIIF
        Then the alert banner responsible with alerting the user should be visible
        """

        file = FileFactory(
            FileName="open_file.docx", ffid_metadata__Extension=None
        )

        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        banner = soup.find("h2", string="Unable to display this record")
        assert banner is not None

    @mock_aws
    def test_record_alert_banner_not_visible_for_convertible_extension(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is compatible with IIIF but is convertible
        Then the alert banner responsible with alerting the user should NOT be visible
        """

        file = FileFactory(ffid_metadata__PUID="fmt/40")
        bucket_name = "test_bucket"

        app.config["ACCESS_COPY_BUCKET"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        banner = soup.find("h2", string="Unable to display this record")
        assert banner is None

    @mock_aws
    def test_record_record_alert_banner_is_visible_when_unsupported_file_extension_and_non_convertible(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is not compatible with IIIF and not in convertible_extensions
        Then the alert banner responsible with alerting the user should be visible
        """

        file = FileFactory(ffid_metadata__Extension="xlsxx")

        bucket_name = "test_bucket"

        app.config["ACCESS_COPY_BUCKET"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        banner = soup.find("h2", string="Unable to display this record")
        assert banner is not None

    @mock_aws
    def test_record_record_alert_banner_is_not_visible_when_supported_file_extension(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is compatible with IIIF
        Then the alert banner responsible with alerting the user should NOT be visible
        """

        file = FileFactory(ffid_metadata__PUID="fmt/276")
        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        banner = soup.find("h2", string="Unable to display this record")
        assert banner is None

    def test_record_standard_user_with_perms_can_download_record_without_citeable_reference(
        self, app, client: FlaskClient, mock_standard_user, jinja_env
    ):
        """
        Given a File in the database
        When a permitted standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should see record download component
        on the page
        """
        file = FileFactory(CiteableReference=None)
        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()
        expected_download_html = (
            expected_download_html_without_citeable_reference(
                jinja_env, file.FileId, file.FileName
            )
        )

        assert_contains_html(
            expected_download_html, html, "div", {"class": "rights-container"}
        )

    @mock_aws
    def test_record_standard_user_with_perms_can_download_record_with_citeable_reference(
        self, app, client: FlaskClient, mock_standard_user, jinja_env
    ):
        """
        Given a File in the database
        When a permitted standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should see record download component
        on the page
        """
        file = FileFactory(
            FileName="open_file.docx",
            CiteableReference="first_body/ABCDE",
            ffid_metadata__Extension="docx",
        )
        download_filename = (
            f"{file.CiteableReference}.{file.ffid_metadata.Extension}"
        )
        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_download_html = expected_download_html_with_citeable_reference(
            jinja_env, file.FileId, download_filename, file.FileName
        )

        assert_contains_html(
            expected_download_html, html, "div", {"class": "rights-container"}
        )

    def test_record_standard_users_with_perms_can_see_download_button(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with download permissions requests the record page
        Then the response status code should be 200
        And the HTML content should show the download button
        And the download button should link to the correct download URL
        And the rights container should be visible on the page
        """
        file = FileFactory()
        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")

        button = soup.find(
            "a", string=lambda text: text and "Download record" in text
        )
        assert button is not None, (
            "Download button should be visible for a user with download permissions"
        )

        assert button["href"] == f"/download/{file.FileId}", (
            "Download button should link to the correct download URL"
        )

        rights_container = soup.find("div", {"class": "rights-container"})
        assert rights_container is not None, (
            "Rights container should be visible for a user with download permissions"
        )

    def test_record_standard_user_without_perms_cant_see_download_button(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with no permissions requests the record page
        Then the response status code should be 200
        And the HTML content should NOT see record download component
        on the page
        """
        file = FileFactory()
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        button = soup.find(
            "a", string=lambda text: text and "Download record" in text
        )

        assert button is None

    def test_record_aau_user_without_perms_cant_see_download_button(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a File in the database
        When a standard user with no permissions requests the record page
        Then the response status code should be 200
        And the HTML content should NOT see record download component
        on the page
        """
        file = FileFactory()
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        button = soup.find("a", string="Download record")
        assert button is None

    @mock_aws
    def test_record_summary_list_open_file(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
            and record closure type is 'Open' (never closed)
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = FileFactory()
        metadata_values = {
            "description": ("description", "open document file"),
            "closure_type": ("closure_type", "Open"),
            "end_date": ("end_date", "2023-01-15"),
            "date_last_modified": ("date_last_modified", "2023-01-15"),
            "former_reference": ("former_reference_department", "-"),
            "translated_title": ("file_name_translation", "-"),
            "related_material": ("related_material", "-"),
            "restrictions_on_use": ("restrictions_on_use", "-"),
            "note": ("note", "-"),
            "held_by": ("held_by", "The National Archives, Kew"),
            "legal_status": ("legal_status", "Public record(s)"),
            "rights_copyright": ("rights_copyright", "Crown copyright"),
            "language": ("language", "English"),
        }
        metadata_by_key = {
            key: FileMetadataFactory(file=file, PropertyName=prop, Value=value)
            for key, (prop, value) in metadata_values.items()
        }
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)
        date_last_modified = datetime.strptime(
            metadata_by_key["date_last_modified"].Value, db_date_format
        ).strftime(python_date_format)
        response = client.get(f"{self.route_url}/{file.FileId}#record-details")
        assert response.status_code == 200
        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        def assert_summary_row(key_text, value_text):
            rows = summary_list.find_all(
                "div", class_="govuk-summary-list__row--record"
            )
            for row in rows:
                dt = row.find(
                    "dt", class_="govuk-summary-list__key--record-table"
                )
                dd = row.find("dd", class_="govuk-summary-list__value--record")
                if dt and dt.get_text(strip=True) == key_text:
                    assert dd is not None and value_text in dd.get_text(
                        strip=True
                    )
                    if len(value_text) > 45:
                        span = row.find(
                            "span", class_="govuk-summary-list-long-word"
                        )
                        assert "govuk-summary-list-long-word" in span["class"]
                    else:
                        span = row.find(
                            "span", class_="govuk-summary-list-short-word"
                        )
                        assert "govuk-summary-list-short-word" in span["class"]
                    return
            assert False, f"Summary row with key '{key_text}' not found"

        assert_summary_row("Date of record", date_last_modified)
        assert_summary_row(
            "Transferring body", file.consignment.series.body.Name
        )
        assert_summary_row("Series reference", file.consignment.series.Name)
        assert_summary_row(
            "Consignment reference", file.consignment.ConsignmentReference
        )
        assert_summary_row("File reference", file.FileReference)
        assert_summary_row(
            "Former reference", metadata_by_key["former_reference"].Value
        )
        assert_summary_row(
            "Translated file name", metadata_by_key["translated_title"].Value
        )
        assert_summary_row(
            "Related material", metadata_by_key["related_material"].Value
        )
        assert_summary_row(
            "Restrictions on use", metadata_by_key["restrictions_on_use"].Value
        )
        assert_summary_row("Note", metadata_by_key["note"].Value)
        assert_summary_row("Held by", metadata_by_key["held_by"].Value)
        assert_summary_row(
            "Legal status", metadata_by_key["legal_status"].Value
        )
        assert_summary_row(
            "Rights copyright", metadata_by_key["rights_copyright"].Value
        )
        assert_summary_row("Language", metadata_by_key["language"].Value)

    @mock_aws
    def test_record_metadata_with_open_record_status(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user navigates to the record page with the ID of an open record
            and record closure type is 'Open' (never closed, no closure_start_date)
        Then the response status code should be 200
        And the HTML content should show only the fields for open records
        And the closed-record-only fields should not be visible
        """
        file = FileFactory()

        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        summary_list_text = summary_list.get_text(strip=True)

        expected_fields = [
            "File name",
            "Description",
            "Status",
            "Date of record",
            "Transferring body",
            "Series reference",
            "Consignment reference",
            "File reference",
            "Former reference",
            "Translated file name",
            "Related material",
            "Restrictions on use",
            "Note",
            "Held by",
            "Legal status",
            "Rights copyright",
            "Language",
        ]
        for field in expected_fields:
            assert field in summary_list_text, (
                f"Expected field '{field}' to be visible for an open record"
            )

        closed_only_fields = [
            "Alternative file name",
            "Alternative description",
            "Opening date",
            "Closure start date",
            "Closure period",
            "FOI exemption code(s)",
        ]
        for field in closed_only_fields:
            assert field not in summary_list_text, (
                f"Field '{field}' should not be visible for a purely open record"
            )

    @mock_aws
    def test_record_summary_list_open_closed_before_file(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
            and record closure type is 'Open' (once closed or close before)
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = FileFactory()
        metadata_values = {
            "alternative_title": ("title_alternate", "alternate title"),
            "description": ("description", "open once closed document file"),
            "alternative_description": ("description_alternate", "-"),
            "closure_type": ("closure_type", "Open"),
            "end_date": ("end_date", "2023-01-15"),
            "date_last_modified": ("date_last_modified", "2023-01-15"),
            "opening_date": ("opening_date", "2023-02-25"),
            "closure_start_date": ("closure_start_date", "2023-01-15"),
            "closure_period": ("closure_period", "10"),
            "foi_exemption_code": ("foi_exemption_code", "14(2)(b)"),
            "former_reference": (
                "former_reference_department",
                "former reference",
            ),
            "translated_title": ("file_name_translation", "-"),
            "related_material": ("related_material", "-"),
            "restrictions_on_use": ("restrictions_on_use", "-"),
            "note": ("note", "-"),
            "held_by": ("held_by", "The National Archives, Kew"),
            "legal_status": ("legal_status", "Public record(s)"),
            "rights_copyright": ("rights_copyright", "Crown copyright"),
            "language": ("language", "English"),
        }
        metadata_by_key = {
            key: FileMetadataFactory(file=file, PropertyName=prop, Value=value)
            for key, (prop, value) in metadata_values.items()
        }
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)
        closure_start_date = datetime.strptime(
            metadata_by_key["closure_start_date"].Value, db_date_format
        ).strftime(python_date_format)
        date_last_modified = datetime.strptime(
            metadata_by_key["date_last_modified"].Value, db_date_format
        ).strftime(python_date_format)
        response = client.get(f"{self.route_url}/{file.FileId}#record-details")
        assert response.status_code == 200
        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        def assert_summary_row(key_text, value_text):
            rows = summary_list.find_all(
                "div", class_="govuk-summary-list__row--record"
            )
            for row in rows:
                dt = row.find(
                    "dt", class_="govuk-summary-list__key--record-table"
                )
                dd = row.find("dd", class_="govuk-summary-list__value--record")
                if dt and dt.get_text(strip=True) == key_text:
                    assert dd is not None and value_text in dd.get_text(
                        strip=True
                    )
                    if key_text == "Status":
                        return
                    if len(value_text) > 45:
                        span = row.find(
                            "span", class_="govuk-summary-list-long-word"
                        )
                        assert "govuk-summary-list-long-word" in span["class"]
                    else:
                        span = row.find(
                            "span", class_="govuk-summary-list-short-word"
                        )
                        assert "govuk-summary-list-short-word" in span["class"]
                    return
            assert False, f"Summary row with key '{key_text}' not found"

        assert_summary_row("File name", file.FileName)
        assert_summary_row(
            "Alternative file name", metadata_by_key["alternative_title"].Value
        )
        assert_summary_row("Description", metadata_by_key["description"].Value)
        assert_summary_row("Citeable reference", str(file.CiteableReference))
        assert_summary_row(
            "Alternative description",
            metadata_by_key["alternative_description"].Value,
        )
        assert_summary_row("Status", metadata_by_key["closure_type"].Value)
        assert_summary_row("Closure start date", closure_start_date)
        assert_summary_row(
            "Closure period", metadata_by_key["closure_period"].Value + " years"
        )
        assert_summary_row("Date of record", date_last_modified)
        assert_summary_row(
            "FOI exemption code(s)", metadata_by_key["foi_exemption_code"].Value
        )
        assert_summary_row(
            "Transferring body", file.consignment.series.body.Name
        )
        assert_summary_row("Series reference", file.consignment.series.Name)
        assert_summary_row(
            "Consignment reference", file.consignment.ConsignmentReference
        )
        assert_summary_row("File reference", file.FileReference)
        assert_summary_row(
            "Former reference", metadata_by_key["former_reference"].Value
        )
        assert_summary_row(
            "Translated file name", metadata_by_key["translated_title"].Value
        )
        assert_summary_row(
            "Related material", metadata_by_key["related_material"].Value
        )
        assert_summary_row(
            "Restrictions on use", metadata_by_key["restrictions_on_use"].Value
        )
        assert_summary_row("Note", metadata_by_key["note"].Value)
        assert_summary_row("Held by", metadata_by_key["held_by"].Value)
        assert_summary_row(
            "Legal status", metadata_by_key["legal_status"].Value
        )
        assert_summary_row(
            "Rights copyright", metadata_by_key["rights_copyright"].Value
        )
        assert_summary_row("Language", metadata_by_key["language"].Value)

    @mock_aws
    def test_record_summary_list_closed_file(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
            and record closure type is 'Closed'
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = FileFactory()
        metadata_values = {
            "alternative_title": ("title_alternate", "alternate title"),
            "description": ("description", "closed document file"),
            "alternative_description": ("description_alternate", "-"),
            "closure_type": ("closure_type", "Closed"),
            "date_last_modified": ("date_last_modified", "2023-01-15"),
            "opening_date": ("opening_date", "2023-02-25"),
            "closure_start_date": ("closure_start_date", "2023-01-15"),
            "closure_period": ("closure_period", "10"),
            "foi_exemption_code": ("foi_exemption_code", "14(2)(b)"),
            "former_reference": (
                "former_reference_department",
                "former reference",
            ),
            "translated_title": ("file_name_translation", "-"),
            "related_material": ("related_material", "-"),
            "restrictions_on_use": ("restrictions_on_use", "-"),
            "note": ("note", "-"),
            "held_by": ("held_by", "The National Archives, Kew"),
            "legal_status": ("legal_status", "Public record(s)"),
            "rights_copyright": ("rights_copyright", "Crown copyright"),
            "language": ("language", "English"),
        }
        metadata_by_key = {
            key: FileMetadataFactory(file=file, PropertyName=prop, Value=value)
            for key, (prop, value) in metadata_values.items()
        }
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)
        closure_start_date = datetime.strptime(
            metadata_by_key["closure_start_date"].Value, db_date_format
        ).strftime(python_date_format)
        date_last_modified = datetime.strptime(
            metadata_by_key["date_last_modified"].Value, db_date_format
        ).strftime(python_date_format)
        response = client.get(f"{self.route_url}/{file.FileId}#record-details")
        assert response.status_code == 200
        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        def assert_summary_row(key_text, value_text):
            rows = summary_list.find_all(
                "div", class_="govuk-summary-list__row--record"
            )
            for row in rows:
                dt = row.find(
                    "dt", class_="govuk-summary-list__key--record-table"
                )
                dd = row.find("dd", class_="govuk-summary-list__value--record")
                if dt and dt.get_text(strip=True) == key_text:
                    if key_text == "Status":
                        return
                    assert dd is not None and value_text in dd.get_text(
                        strip=True
                    )
                    if len(value_text) > 45:
                        span = row.find(
                            "span", class_="govuk-summary-list-long-word"
                        )
                        assert "govuk-summary-list-long-word" in span["class"]
                    else:
                        span = row.find(
                            "span", class_="govuk-summary-list-short-word"
                        )
                        assert "govuk-summary-list-short-word" in span["class"]
                    return
            assert False, f"Summary row with key '{key_text}' not found"

        assert_summary_row("File name", file.FileName)
        assert_summary_row(
            "Alternative file name", metadata_by_key["alternative_title"].Value
        )
        assert_summary_row("Description", metadata_by_key["description"].Value)
        assert_summary_row("Citeable reference", str(file.CiteableReference))
        assert_summary_row(
            "Alternative description",
            metadata_by_key["alternative_description"].Value,
        )
        assert_summary_row("Status", metadata_by_key["closure_type"].Value)
        assert_summary_row("Closure start date", closure_start_date)
        assert_summary_row(
            "Closure period", metadata_by_key["closure_period"].Value + " years"
        )
        assert_summary_row("Date of record", date_last_modified)
        assert_summary_row(
            "FOI exemption code(s)", metadata_by_key["foi_exemption_code"].Value
        )
        assert_summary_row(
            "Transferring body", file.consignment.series.body.Name
        )
        assert_summary_row("Series reference", file.consignment.series.Name)
        assert_summary_row(
            "Consignment reference", file.consignment.ConsignmentReference
        )
        assert_summary_row("File reference", file.FileReference)
        assert_summary_row(
            "Former reference", metadata_by_key["former_reference"].Value
        )
        assert_summary_row(
            "Translated file name", metadata_by_key["translated_title"].Value
        )
        assert_summary_row(
            "Related material", metadata_by_key["related_material"].Value
        )
        assert_summary_row(
            "Restrictions on use", metadata_by_key["restrictions_on_use"].Value
        )
        assert_summary_row("Note", metadata_by_key["note"].Value)
        assert_summary_row("Held by", metadata_by_key["held_by"].Value)
        assert_summary_row(
            "Legal status", metadata_by_key["legal_status"].Value
        )
        assert_summary_row(
            "Rights copyright", metadata_by_key["rights_copyright"].Value
        )
        assert_summary_row("Language", metadata_by_key["language"].Value)

    @mock_aws
    def test_record_metadata_with_closed_record_status(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user navigates to the record page with the ID of a closed record
            and record closure type is 'Closed'
        Then the response status code should be 200
        And the HTML content should show 'Closed' as the Status field value
        And all closed-record-specific fields should be visible
        And open-record-only fields should not be visible
        """
        file = FileFactory()
        metadata_values = {
            "alternative_title": ("title_alternate", "alternate title"),
            "description": ("description", "closed document file"),
            "alternative_description": ("description_alternate", "-"),
            "closure_type": ("closure_type", "Closed"),
            "date_last_modified": ("date_last_modified", "2023-01-15"),
            "closure_start_date": ("closure_start_date", "2023-01-15"),
            "closure_period": ("closure_period", "10"),
            "foi_exemption_code": ("foi_exemption_code", "14(2)(b)"),
            "former_reference": (
                "former_reference_department",
                "former reference",
            ),
            "translated_title": ("file_name_translation", "-"),
            "related_material": ("related_material", "-"),
            "restrictions_on_use": ("restrictions_on_use", "-"),
            "note": ("note", "-"),
            "held_by": ("held_by", "The National Archives, Kew"),
            "legal_status": ("legal_status", "Public record(s)"),
            "rights_copyright": ("rights_copyright", "Crown copyright"),
            "language": ("language", "English"),
        }
        metadata_by_key = {
            key: FileMetadataFactory(file=file, PropertyName=prop, Value=value)
            for key, (prop, value) in metadata_values.items()
        }
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        summary_list_text = summary_list.get_text(strip=True)

        rows = summary_list.find_all(
            "div", class_="govuk-summary-list__row--record"
        )
        status_row_found = False
        for row in rows:
            dt = row.find("dt", class_="govuk-summary-list__key--record-table")
            dd = row.find("dd", class_="govuk-summary-list__value--record")
            if dt and dt.get_text(strip=True) == "Status":
                assert dd is not None
                assert metadata_by_key["closure_type"].Value in dd.get_text(
                    strip=True
                ), "Status field value should be 'Closed'"
                status_row_found = True
                break
        assert status_row_found, "Status row not found in summary list"

        expected_fields = [
            "File name",
            "Alternative file name",
            "Description",
            "Alternative description",
            "Status",
            "Closure start date",
            "Closure period",
            "Date of record",
            "FOI exemption code(s)",
            "Transferring body",
            "Series reference",
            "Consignment reference",
            "File reference",
            "Former reference",
            "Translated file name",
            "Related material",
            "Restrictions on use",
            "Note",
            "Held by",
            "Legal status",
            "Rights copyright",
            "Language",
        ]
        for field in expected_fields:
            assert field in summary_list_text, (
                f"Expected field '{field}' to be visible for a closed record"
            )

    @mock_aws
    def test_record_view_renders(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record render page
        Then the response status code should be 200
        And the HTML content should show the record view tab with
        universal viewer displayed
        """
        mock_all_access_user(client)

        file = FileFactory(ffid_metadata__PUID="fmt/276")

        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"{self.route_url}/{file.FileId}#record-view")

        assert response.status_code == 200

        html = response.data.decode()

        search_html = """
        <div class="uv" id="uv">
        </div>
        """

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "uv"},
        )

    @mock_aws
    def test_record_summary_list_renders_evidence_provided_by_when_present(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File with evidence_provided_by metadata
        When the record details page is rendered
        Then the 'Evidence provided by' row is shown with the metadata value
        """
        file = FileFactory()

        evidence_value = "Evidence provided by test"
        FileMetadataFactory(
            file=file,
            PropertyName="evidence_provided_by",
            Value=evidence_value,
        )

        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")
        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        rows = summary_list.find_all(
            "div", class_="govuk-summary-list__row--record"
        )
        for row in rows:
            dt = row.find("dt", class_="govuk-summary-list__key--record-table")
            dd = row.find("dd", class_="govuk-summary-list__value--record")
            if dt and dt.get_text(strip=True) == "Evidence provided by":
                assert dd is not None
                assert evidence_value in dd.get_text(strip=True)
                return

        assert False, "Summary row with key 'Evidence provided by' not found"

    @mock_aws
    def test_record_summary_list_hides_evidence_provided_by_when_missing(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File with no evidence_provided_by metadata
        When the record details page is rendered
        Then the 'Evidence provided by' row is not shown at all
        """
        file = FileFactory()

        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")
        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")
        summary_list = soup.find("dl", class_="govuk-summary-list--record")
        assert summary_list is not None

        assert "Evidence provided by" not in summary_list.get_text(strip=True)
