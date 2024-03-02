from datetime import datetime

from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


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

    def test_record_top_search(
        self, client: FlaskClient, mock_superuser, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should show top search component
        on the page
        """
        mock_superuser(client)

        file = record_files[0]["file_object"]

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        search_html = """<div class="search__container govuk-grid-column-full">
        <div class="search__container__content">
            <p class="govuk-body search__heading">Search for digital records</p>
            <form method="get" action="/search">
                <div class="govuk-form-group govuk-form-group__search-form">
                    <label for="searchInput"></label>
                    <input class="govuk-input govuk-!-width-three-quarters"
                           id="searchInput"
                           name="query"
                           type="text"
                           value="">
                    <button class="govuk-button govuk-button__search-button"
                            data-module="govuk-button"
                            type="submit">Search</button>
                </div>
                <p class="govuk-body-s">
                    Search by file name, transferring body, series or consignment reference.
                </p>
            </form>
        </div>
    </div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "search__container govuk-grid-column-full"},
        )

    def test_record_breadcrumbs(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should show the breadcrumb values as
         Everything > transferring body > series > consignment reference > file name
        on the page
        """
        file = record_files[0]["file_object"]
        mock_standard_user(client, file.consignment.series.body.Name)

        browse_all_route_url = "/browse"
        browse_transferring_body_route_url = (
            f"{browse_all_route_url}/transferring_body"
        )
        browse_series_route_url = f"{browse_all_route_url}/series"
        browse_consignment_route_url = f"{browse_all_route_url}/consignment"

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-grid-column-full govuk-grid-column-full__page-nav">
        <p class="govuk-body-m govuk-body-m__record-view">You are viewing</p>

        <div class="govuk-breadcrumbs govuk-breadcrumbs--file">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{browse_all_route_url}">Everything</a>
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

    def test_record_record_arrangement(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should see record arrangement based on file path
        on the page
        """
        file = record_files[0]["file_object"]
        mock_standard_user(client, file.consignment.series.body.Name)

        record_path_details = file.FilePath.split("/")

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_arrangement_html = f"""
        <div class="record-container">
            <h3 class="govuk-heading-m govuk-heading-m__record-header">Record arrangement</h3>
            <ol>
                <li class="govuk-body govuk-body__record-arrangement-list">{record_path_details[0]}</li>
                <li class=" govuk-body govuk-body__record-arrangement-list">{record_path_details[1]}</li>
                <li class="govuk-body govuk-body__record-arrangement-list">{record_path_details[2]}</li>
                <li class="govuk-body govuk-body__record-arrangement-list">{record_path_details[3]}</li>
            </ol>
        </div>
        """

        assert_contains_html(
            expected_arrangement_html,
            html,
            "div",
            {"class": "record-container"},
        )

    def test_record_download_record(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
        Then the response status code should be 200
        And the HTML content should see record download component
        on the page
        """
        file = record_files[0]["file_object"]
        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_download_html = f"""
        <div class="rights-container">
            <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
            <a href="/download/{file.FileId}"
                class="govuk-button govuk-button__download--record"
                data-module="govuk-button">Download record</a>
            <p class="govuk-body govuk-body--terms-of-use">
                Refer to <a href="/terms-of-use" class="govuk-link govuk-link--ayr">Terms of use.</a>
            </p>
        </div>
        """

        assert_contains_html(
            expected_download_html, html, "div", {"class": "rights-container"}
        )

    def test_record_summary_list_open_file(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
            and record closure type is 'Open' (never closed)
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = record_files[0]["file_object"]

        mock_standard_user(client, file.consignment.series.body.Name)

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
                        <div class="govuk-summary-list__row"></div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {record_files[0]["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--green"><strong>{record_files[0]["closure_type"].Value}</strong></span>
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Record date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {datetime.strptime(record_files[0]["date_last_modified"].Value,"%Y-%m-%d").strftime('%d/%m/%Y')}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment ref.</dt>
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
                        {record_files[0]["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[0]["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[0]["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[0]["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[0]["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[0]["language"].Value}
                </dd>
            </div>
                    </dl>"""

        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
        )

    def test_record_summary_list_open_closed_before_file(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
            and record closure type is 'Open' (once closed or close before)
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = record_files[1]["file_object"]

        mock_standard_user(client, file.consignment.series.body.Name)

        opening_date = datetime.strptime(
            record_files[1]["opening_date"].Value, "%Y-%m-%d"
        ).strftime("%d/%m/%Y")
        closure_start_date = datetime.strptime(
            record_files[1]["closure_start_date"].Value, "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
                        <div class="govuk-summary-list__row"></div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["alternative_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["alternative_description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--green"><strong>{record_files[1]["closure_type"].Value}</strong></span>
<span>Record opening date {opening_date}</span></dd>
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
                            {record_files[1]["closure_period"].Value + " years"}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Record date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {datetime.strptime(record_files[1]["date_last_modified"].Value,"%Y-%m-%d").strftime('%d/%m/%Y')}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">FOI exemption code(s)</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["foi_exemption_code"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series</dt>
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
                            {record_files[1]["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {record_files[1]["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[1]["language"].Value}
                </dd>
            </div>
                    </dl>"""

        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
        )

    def test_record_summary_list_closed_file(
        self, client: FlaskClient, mock_standard_user, record_files
    ):
        """
        Given a File in the database
        When a standard user with request to view the record page
            and record closure type is 'Closed'
        Then the response status code should be 200
        And the HTML content should see summary list with specific items
        on the page
        """
        file = record_files[2]["file_object"]

        mock_standard_user(client, file.consignment.series.body.Name)

        opening_date = datetime.strptime(
            record_files[2]["opening_date"].Value, "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_record_summary_html = f"""
        <dl class="govuk-summary-list govuk-summary-list--record">
                        <div class="govuk-summary-list__row"></div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.FileName}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["alternative_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Alternative description</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["alternative_description"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--red"><strong>{record_files[2]["closure_type"].Value}</strong></span>
<span>Record opening date {opening_date}</span></dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure start date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {datetime.strptime(record_files[2]["closure_start_date"].Value,"%Y-%m-%d").strftime('%d/%m/%Y')}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Closure period</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["closure_period"].Value + " years"}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Record date</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {datetime.strptime(record_files[2]["date_last_modified"].Value,"%Y-%m-%d").strftime('%d/%m/%Y')}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">FOI exemption code(s)</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["foi_exemption_code"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {file.consignment.series.body.Name}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Series</dt>
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
                            {record_files[2]["former_reference"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Translated title</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                        {record_files[2]["translated_title"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["held_by"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["legal_status"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["rights_copyright"].Value}
                </dd>
            </div>
            <div class="govuk-summary-list__row govuk-summary-list__row--record">
                <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
                <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                            {record_files[2]["language"].Value}
                </dd>
            </div>
                    </dl>"""

        assert_contains_html(
            expected_record_summary_html,
            html,
            "dl",
            {"class": "govuk-summary-list govuk-summary-list--record"},
        )
