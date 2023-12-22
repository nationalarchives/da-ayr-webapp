from bs4 import BeautifulSoup

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


def test_valid_id_returns_expected_html(client):
    """
    Given a file with id, file_id, and associated metadata,
    When a GET request is made to `record/file_id`
    Then the response contains html including the record's expected metadata
    """
    file = FileFactory(FileName="test_file.txt", FileType="file")

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
            file_metadata=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    response = client.get(f"/record/{file.FileId}")

    assert response.status_code == 200

    html = response.data.decode()

    soup = BeautifulSoup(html, "html.parser")

    expected_breadcrumbs_html = f"""
    <div class="govuk-grid-column-full govuk-grid-column-full__page-nav">
    <p class="govuk-body-m govuk-body-m__record-view">You are viewing</p>
    <div class="govuk-breadcrumbs govuk-breadcrumbs--record">
        <ol class="govuk-breadcrumbs__list">
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record"
                href="/browse?transferring_body_id={file.file_consignments.consignment_bodies.BodyId}">{file.file_consignments.consignment_bodies.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record"
                href="/browse?series_id={file.file_consignments.consignment_series.SeriesId}">{file.file_consignments.consignment_series.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record"
                href="/browse?consignment_id={file.ConsignmentId}">{file.file_consignments.ConsignmentReference}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record">test_file.txt</a>
            </li>
        </ol>
        </div>
    </div>
    """

    breadcrumbs_soup = soup.find(
        "div",
        {"class": "govuk-grid-column-full govuk-grid-column-full__page-nav"},
    )
    expected_breadcrumbs_soup = BeautifulSoup(
        expected_breadcrumbs_html, "html.parser"
    )

    assert expected_breadcrumbs_soup.prettify() == breadcrumbs_soup.prettify()

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
                {file.file_consignments.consignment_bodies.Name}
            </dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment ID</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">
                {file.file_consignments.ConsignmentId}
            </dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Description</dt>
            <dd class="govuk-summary-list__value govuk-summary-list__value--record">Test description</dd>
        </div>
        <div class="govuk-summary-list__row govuk-summary-list__row--record">
            <dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Date last modified</dt>
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

    expected_record_summary_soup = BeautifulSoup(
        expected_record_summary_html, "html.parser"
    )

    record_summary_soup = soup.find(
        "dl",
        {"class": "govuk-summary-list govuk-summary-list--record"},
    )

    assert (
        expected_record_summary_soup.prettify()
        == record_summary_soup.prettify()
    )

    assert (
        b'<button class="govuk-button govuk-button__download--record" data-module="govuk-button">'
        b"Download record</button>" in response.data
    )

    assert (
        b'<p class="govuk-body govuk-body--terms-of-use">'
        b'Refer to <a href="/terms-of-use" class="govuk-link">Terms of use.</a></p>'
        in response.data
    )

    assert (
        b'<li class="govuk-body govuk-body__record-arrangement-list">'
        b"political parties panel - notes of meeting 1 - 12 September 2003.doc</li>"
        in response.data
    )
