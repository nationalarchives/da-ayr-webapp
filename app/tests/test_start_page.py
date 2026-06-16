from app.tests.assertions import assert_contains_html


def test_start_page(client, jinja_env):
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

    expected_button_html = jinja_env.from_string("""
    {% from 'govuk_frontend_jinja/components/button/macro.html' import govukButton %}
    {{ govukButton({
        'text': 'Start now',
        'href': '/sign-in',
        'isStartButton': true,
        'classes': 'govuk-button--start'
    }) }}
""").render()
    assert_contains_html(
        expected_button_html, html, "a", {"class": "govuk-button--start"}
    )
