from app.tests.assertions import assert_contains_html


def test_signed_out_page(client):
    response = client.get("/signed-out")

    assert response.status_code == 200

    html = response.data.decode()

    assert (
        b'<h1 class="govuk-heading-l">You have signed out</h1>' in response.data
    )
    assert (
        b'<p class="govuk-body-l">Thank you for using Access Your Records.</p>'
        in response.data
    )

    expected_button_html = (
        '<a href="/sign-in" role="button" class="govuk-button govuk-button--sign-in-again" '
        'data-module="govuk-button">Sign in</a>'
    )
    assert_contains_html(
        expected_button_html,
        html,
        "a",
        {"class": "govuk-button--sign-in-again"},
    )
