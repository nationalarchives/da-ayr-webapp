from app.tests.assertions import assert_contains_html


def test_header_links_render(client):
    """
    Given a user has loaded the homepage.
    Ensure that the header has loaded and contains the correct links
    and classnames with hrefs
    """

    response = client.get("/")

    assert response.status_code == 200

    html = response.data.decode()

    header_html = """<header class="govuk-header" data-module="govuk-header" role="banner">
 <div class="govuk-header__container govuk-header__container--ayr govuk-width-container">
  <div class="govuk-header__logo">
   <a class="govuk-header__link govuk-header__link--homepage" href="/browse">
    <span class="govuk-header__logotype-text govuk-header__logotype--ayr">
     Access Your Records (AYR)
    </span>
   </a>
  </div>
  <div class="govuk-header__content govuk-header__content--tna">
   Delivered by
   <a class="govuk-header__link govuk-header__link--tna" href="https://www.nationalarchives.gov.uk/">
    The National Archives
   </a>
  </div>
 </div>
</header>"""

    assert_contains_html(
        header_html,
        html,
        "header",
        {"class": "govuk-header"},
    )
