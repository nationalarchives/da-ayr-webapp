from app.tests.assertions import assert_contains_html
from app.tests.factories import FileFactory, FileMetadataFactory


def test_invalid_id_raises_404(client):
    """
    Given a UUID, `invalid_file_id`, not corresponding to the id
        of a file in the database
    When a GET request is made to `/record/invalid_file_id`
    Then a 404 http response is returned
    """
    response = client.get("/record/some-id")

    assert response.status_code == 404


def test_returns_record_page_for_user_with_access_to_files_transferring_body(
    client, mock_standard_user
):
    """
    Given a File in the database
    When a standard user with access to the file's transferring body makes a
        request to view the record page
    Then the response status code should be 200
    And the HTML content should contain specific elements
        related to the record
    """
    file = FileFactory(
        FileName="test_file.txt",
        FilePath="data/content/folder_a/test_file.txt",
        FileType="file",
    )

    mock_standard_user(client, file.consignment.series.body.Name)

    metadata = {
        "date_last_modified": "2023-02-25T10:12:47",
        "closure_type": "Closed",
        "description": "Test description",
        "held_by": "Test holder",
        "legal_status": "Test legal status",
        "rights_copyright": "Test copyright",
        "language": "English",
    }

    [
        FileMetadataFactory(
            file=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    response = client.get(f"/record/{file.FileId}")

    assert response.status_code == 200

    html = response.data.decode()

    expected_breadcrumbs_html = f"""
    <div class="govuk-grid-column-full govuk-grid-column-full__page-nav">
    <p class="govuk-body-m govuk-body-m__record-view">You are viewing</p>

    <div class="govuk-breadcrumbs govuk-breadcrumbs--file">
        <ol class="govuk-breadcrumbs__list">
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record--transferring-body"
                href="/browse/transferring_body/{file.consignment.series.body.BodyId}">{file.consignment.series.body.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record--series"
                href="/browse/series/{file.consignment.series.SeriesId}">{file.consignment.series.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record--consignment"
                href="/browse/consignment/{file.ConsignmentId}">{file.consignment.ConsignmentReference}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">test_file.txt</span>
            </li>
        </ol>
        </div>
    </div>
    """

    assert_contains_html(
        expected_breadcrumbs_html,
        html,
        "div",
        {"class": "govuk-grid-column-full govuk-grid-column-full__page-nav"},
    )

    expected_record_summary_html = f"""
    <dl class="govuk-summary-list govuk-summary-list--record">
        <div class="govuk-summary-list__row"></div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Filename</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">test_file.txt</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Status</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                <span class="govuk-tag govuk-tag--red">Closed</span>
            </dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Transferring body</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                {file.consignment.series.body.Name}
            </dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment ID</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                {file.consignment.ConsignmentId}
            </dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">Test description</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Record date</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">2023-02-25T10:12:47</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Held by</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">Test holder</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Legal status</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">Test legal status</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Rights copyright</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">Test copyright</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Language</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">English</dd>
        </div>
    </dl>
    """

    assert_contains_html(
        expected_record_summary_html,
        html,
        "dl",
        {"class": "govuk-summary-list govuk-summary-list--record"},
    )

    expected_arrangement_html = """
    <div class="record-container">
        <h3 class="govuk-heading-m govuk-heading-m__record-header">Record arrangement</h3>
        <ol>
            <li class="govuk-body govuk-body__record-arrangement-list">data</li>
            <li class=" govuk-body govuk-body__record-arrangement-list">content</li>
            <li class="govuk-body govuk-body__record-arrangement-list">folder_a</li>
            <li class="govuk-body govuk-body__record-arrangement-list">test_file.txt</li>
        </ol>
    </div>
    """

    assert_contains_html(
        expected_arrangement_html, html, "div", {"class": "record-container"}
    )

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


def test_raises_404_for_user_without_access_to_files_transferring_body(
    client, mock_standard_user
):
    """
    Given a File in the database
    When a standard user without access to the file's consignment body makes a
        request to view the record page
    Then the response status code should be 404
    """

    file = FileFactory(
        FileName="test_file.txt",
        FilePath="data/content/folder_a/test_file.txt",
        FileType="file",
    )

    metadata = {
        "date_last_modified": "2023-02-25T10:12:47",
        "closure_type": "Closed",
        "description": "Test description",
        "held_by": "Test holder",
        "legal_status": "Test legal status",
        "rights_copyright": "Test copyright",
        "language": "English",
    }

    [
        FileMetadataFactory(
            file=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    mock_standard_user(client, "different_body")

    response = client.get(f"/record/{file.FileId}")

    assert response.status_code == 404


def test_returns_record_page_for_superuser(client, mock_superuser):
    """
    Given a File in the database
    And a superuser
    When the superuser makes a request to view the record page
    Then the response status code should be 200
    """
    mock_superuser(client)

    file = FileFactory(
        FileName="test_file.txt",
        FilePath="data/content/folder_a/test_file.txt",
        FileType="file",
    )

    metadata = {
        "date_last_modified": "2023-02-25T10:12:47",
        "closure_type": "Closed",
        "description": "Test description",
        "held_by": "Test holder",
        "legal_status": "Test legal status",
        "rights_copyright": "Test copyright",
        "language": "English",
    }

    [
        FileMetadataFactory(
            file=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    response = client.get(f"/record/{file.FileId}")

    assert response.status_code == 200


def test_record_top_search(client, mock_superuser):
    mock_superuser(client)

    file = FileFactory(
        FileName="test_file.txt",
        FilePath="data/content/folder_a/test_file.txt",
        FileType="file",
    )

    metadata = {
        "date_last_modified": "2023-02-25T10:12:47",
        "closure_type": "Closed",
        "description": "Test description",
        "held_by": "Test holder",
        "legal_status": "Test legal status",
        "rights_copyright": "Test copyright",
        "language": "English",
    }

    [
        FileMetadataFactory(
            file=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    response = client.get(f"/record/{file.FileId}")

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
                Search using a record metadata term, for example – transferring body, series,
                consignment
                ref etc.
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
