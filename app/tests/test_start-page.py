def test_start_page(client):
    response = client.get("/start-page")

    assert response.status_code == 200
    assert (
        b'<h2 class="govuk-heading-m govuk-heading-m--start">Before you start</h2>'
        in response.data
    )
    assert (
        b'<h1 class="govuk-heading-l govuk-heading-l--start">Access your records</h1>'
        in response.data
    )
    assert (
        b'<a href="#" role="button" draggable="false" '
        b'class="govuk-button govuk-button--start" '
        b'data-module="govuk-button">Start now'
    ) in response.data
