from app.tests.assertions import assert_contains_html


def test_signed_out_page(client, jinja_env):
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

    expected_button_html = jinja_env.from_string("""
        {% from 'govuk_frontend_jinja/components/button/macro.html' import govukButton %}
        {{ govukButton({
            'text': "Sign in",
            'href': "/sign-in",
            'classes': "govuk-button--sign-in-again"
        }) }}
    """).render()
    assert_contains_html(
        expected_button_html,
        html,
        "a",
        {"class": "govuk-button--sign-in-again"},
    )
