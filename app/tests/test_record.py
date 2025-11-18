from datetime import datetime

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
    file_id, file_name_download, file_name
):
    return f"""
        <div class="rights-container">
            <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
            <a href="/download/{file_id}"
                class="govuk-button govuk-button__download--record"
                data-module="govuk-button"
                aria-label="Download record {file_name}">Download record</a>
            <p class="govuk-body govuk-body--download-filename">
                The downloaded record will be named<br>
                <strong>{file_name_download}</strong>
            </p>
            <p class="govuk-body govuk-body--terms-of-use">
                Refer to <a href="/terms-of-use" class="govuk-link govuk-link--ayr">Terms of use.</a>
            </p>
        </div>
        """


def expected_download_html_without_citeable_reference(file_id, file_name):
    return f"""
        <div class="rights-container">
            <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
            <a href="/download/{file_id}"
                class="govuk-button govuk-button__download--record"
                data-module="govuk-button"
                aria-label="Download record {file_name}">Download record</a>
            <p class="govuk-body govuk-body--terms-of-use">
                Refer to <a href="/terms-of-use" class="govuk-link govuk-link--ayr">Terms of use.</a>
            </p>
        </div>
        """


class TestRecord:
    @property
    def route_url(self):
        return "/record"

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
    def test_record_breadcrumbs(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        And the HTML content should show the breadcrumb values as
         All available records > transferring body > series > consignment reference > file name
        on the page
        """

        file = FileFactory()
        bucket_name = "test_bucket"

        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)
        mock_standard_user(client, file.consignment.series.body.Name)

        browse_all_route_url = "/browse"
        browse_transferring_body_route_url = (
            f"{browse_all_route_url}/transferring_body"
        )
        browse_series_route_url = f"{browse_all_route_url}/series"
        browse_consignment_route_url = f"{browse_all_route_url}/consignment"

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-grid-column-full govuk-grid-column-full__page-nav">
        <p class="govuk-body browse__body">You are viewing</p>

        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{browse_all_route_url}">All available records</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record--transferring-body"
                    href="{browse_transferring_body_route_url}/{file.consignment.series.body.BodyId}">{file.consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record--series"
                    href="{browse_series_route_url}/{file.consignment.series.SeriesId}">{file.consignment.series.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record--consignment"
                    href="{browse_consignment_route_url}/{file.ConsignmentId}">{file.consignment.ConsignmentReference}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">{file.FileName}</span>
                </li>
            </ol>
            </div>
        </div>
        """

        assert_contains_html(
            expected_breadcrumbs_html,
            html,
            "div",
            {
                "class": "govuk-grid-column-full govuk-grid-column-full__page-nav"
            },
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

        file = FileFactory(ffid_metadata__Extension="pdf")
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

    @mock_aws
    def test_record_record_alert_banner_is_not_visible_when_supported_file_extension_no_ffid_metadata(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """
        Given a File with no FFID metadata in the database
        When a standard user with request to view the record details page
        Then the response status code should be 200
        If the extension of the File requested is compatible with IIIF
        Then the alert banner responsible with alerting the user should NOT be visible
        """

        file = FileFactory(
            FileName="open_file.pdf", ffid_metadata__Extension=None
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
        assert banner is None

    def test_record_standard_user_with_perms_can_download_record_without_citeable_reference(
        self, app, client: FlaskClient, mock_standard_user
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
                file.FileId, file.FileName
            )
        )

        assert_contains_html(
            expected_download_html, html, "div", {"class": "rights-container"}
        )

    @mock_aws
    def test_record_standard_user_with_perms_can_download_record_with_citeable_reference(
        self, app, client: FlaskClient, mock_standard_user
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
            file.FileId, download_filename, file.FileName
        )

        assert_contains_html(
            expected_download_html, html, "div", {"class": "rights-container"}
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
        button = soup.find("a", string="Download record")

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

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Citeable reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.CiteableReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--green">{metadata_by_key["closure_type"].Value}</span>
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Date of record</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {date_last_modified}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.ConsignmentReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.FileReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Former reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated file name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Related material</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["related_material"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Restrictions on use</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["restrictions_on_use"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Note</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["note"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["language"].Value}
                </dd>
            </div>
                    </dl>"""

        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
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

        opening_date = datetime.strptime(
            metadata_by_key["opening_date"].Value, db_date_format
        ).strftime(python_date_format)
        closure_start_date = datetime.strptime(
            metadata_by_key["closure_start_date"].Value, db_date_format
        ).strftime(python_date_format)
        date_last_modified = datetime.strptime(
            metadata_by_key["date_last_modified"].Value, db_date_format
        ).strftime(python_date_format)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative file name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["alternative_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Citeable reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.CiteableReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["alternative_description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--green">{metadata_by_key["closure_type"].Value}</span>
<p class="ayr-opening-date">Record opening date {opening_date}</p></dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure start date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {closure_start_date}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure period</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["closure_period"].Value + " years"}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Date of record</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {date_last_modified}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">FOI exemption code(s)</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["foi_exemption_code"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.ConsignmentReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.FileReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Former reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated file name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Related material</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["related_material"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Restrictions on use</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["restrictions_on_use"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Note</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["note"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["language"].Value}
                </dd>
            </div>
                    </dl>"""

        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
        )

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

        opening_date = datetime.strptime(
            metadata_by_key["opening_date"].Value, db_date_format
        ).strftime(python_date_format)

        closure_start_date = datetime.strptime(
            metadata_by_key["closure_start_date"].Value, db_date_format
        ).strftime(python_date_format)

        date_last_modified = datetime.strptime(
            metadata_by_key["date_last_modified"].Value, db_date_format
        ).strftime(python_date_format)

        response = client.get(f"{self.route_url}/{file.FileId}#record-details")

        assert response.status_code == 200

        html = response.data.decode()

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative file name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["alternative_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Citeable reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.CiteableReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["alternative_description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--red">{metadata_by_key["closure_type"].Value}</span>
                <p class="ayr-opening-date">Record opening date {opening_date}</p></dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure start date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {closure_start_date}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure period</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["closure_period"].Value + " years"}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Date of record</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {date_last_modified}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">FOI exemption code(s)</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["foi_exemption_code"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.ConsignmentReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">File reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {file.FileReference}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Former reference</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated file name</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Related material</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["related_material"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Restrictions on use</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["restrictions_on_use"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Note</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {metadata_by_key["note"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {metadata_by_key["language"].Value}
                </dd>
            </div>
                    </dl>"""
        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
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

        file = FileFactory(ffid_metadata__Extension="pdf")

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
