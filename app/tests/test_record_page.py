def test_record_page(client):
    response = client.get("/record")

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
