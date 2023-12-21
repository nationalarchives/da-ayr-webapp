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
    file = FileFactory(FileType="file")

    FileMetadataFactory(
        file_metadata=file,
        PropertyName="date_last_modified",
        Value="2023-02-25T10:12:47",
    )
    FileMetadataFactory(
        file_metadata=file, PropertyName="closure_type", Value="Closed"
    )
    FileMetadataFactory(
        file_metadata=file, PropertyName="description", Value="Test description"
    )
    FileMetadataFactory(
        file_metadata=file,
        PropertyName="held_by",
        Value="Test holder",
    )
    FileMetadataFactory(
        file_metadata=file,
        PropertyName="legal_status",
        Value="Test legal status",
    )
    FileMetadataFactory(
        file_metadata=file,
        PropertyName="rights_copyright",
        Value="Test copyright",
    )
    FileMetadataFactory(
        file_metadata=file,
        PropertyName="language",
        Value="English",
    )

    response = client.get(f"/record/{file.FileId}")

    assert response.status_code == 200

    assert (
        b'<a class="govuk-breadcrumbs__link--record" href="#">Electoral Commision</a>'
        in response.data
    )
    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment ID</dt>'
        in response.data
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

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table">'
        b"Filename</dt>" in response.data
    )

    assert (
        b'<dd class="govuk-summary-list__value govuk-summary-list__value--record">'
        in response.data
    )

    assert (
        b' <dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Status</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Transferring body</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Consignment ID</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Description</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Date last modified</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Held by</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Legal status</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Rights copyright</dt>" in response.data
    )

    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table"'
        b">Language</dt>" in response.data
    )
