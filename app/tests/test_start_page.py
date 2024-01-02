from app.tests.assertions import assert_contains_html


def test_start_page(client):
    response = client.get("/")

    assert response.status_code == 200

    html = response.data.decode()

    assert (
        b'<h2 class="govuk-heading-m govuk-heading-m--start">Before you start</h2>'
        in response.data
    )
    assert (
        b'<h1 class="govuk-heading-l govuk-heading-l--start">Access your records</h1>'
        in response.data
    )

    expected_button_html = (
        '<a class="govuk-button govuk-button--start" data-module="govuk-button" '
        'draggable="false" href="/sign-in" role="button">Start now'
        '<svg aria-hidden="true" class="govuk-button__start-icon" '
        'focusable="false" height="19" viewbox="0 0 33 40" width="17.5" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0h13l20 20-20 20H0l20-20z" fill="currentColor"></path>'
        "</svg>"
        "</a>"
    )
    assert_contains_html(
        expected_button_html, html, "a", {"class": "govuk-button"}
    )
