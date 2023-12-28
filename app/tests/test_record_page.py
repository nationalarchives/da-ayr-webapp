from app.tests.assertions import assert_contains_html


def test_record_page(client):
    response = client.get("/record")

    assert response.status_code == 200

    html = response.data.decode()

    assert (
        b'<a class="govuk-breadcrumbs__link--record" href="#">Electoral Commision</a>'
        in response.data
    )
    assert (
        b'<dt class="govuk-summary-list__key govuk-summary-list__key--record-table">Consignment ID</dt>'
        in response.data
    )

    expected_download_html = """
    <div class="rights-container">
        <h3 class="govuk-heading-m govuk-heading-m__rights-header">Rights to access</h3>
        <button class="govuk-button govuk-button__download--record" data-module="govuk-button">
            Download record
        </button>
        <p class="govuk-body govuk-body--terms-of-use">
            Refer to <a href="/terms-of-use" class="govuk-link">Terms of use.</a>
        </p>
    </div>
    """

    assert_contains_html(
        expected_download_html, html, "div", {"class": "rights-container"}
    )

    expected_arrangement_html = (
        '<div class="record-container">'
        '<h3 class="govuk-heading-m govuk-heading-m__record-header">Record arrangement</h3>'
        "<ol>"
        '<li class="govuk-body govuk-body__record-arrangement-list">Electoral commission meeting notes</li>'
        '<li class=" govuk-body govuk-body__record-arrangement-list">2003</li>'
        '<li class="govuk-body govuk-body__record-arrangement-list">September</li>'
        '<li class="govuk-body govuk-body__record-arrangement-list">'
        "political parties panel - notes of meeting 1 - 12 September 2003.doc</li>"
        "</ol>"
        "</div>"
    )

    assert_contains_html(
        expected_arrangement_html, html, "div", {"class": "record-container"}
    )
