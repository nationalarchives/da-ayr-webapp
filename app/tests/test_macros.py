import pytest
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


class TestBanners:
    @property
    def template(self):
        """Dynamically load and return the Jinja2 template."""
        env = Environment(loader=FileSystemLoader("app/templates"))
        return env.get_template("main/macros/banners.html")

    @property
    def macros(self):
        """Access the macros in the template."""
        return self.template.make_module()

    @pytest.mark.parametrize(
        "variant, heading, message, expected_class, expected_heading, expected_message",
        [
            (
                "",
                "Default Heading",
                "Default message",
                "ayr-alert-banner--",
                "Default Heading",
                "Default message",
            ),
            (
                "error",
                "Error Heading",
                "This is an error!",
                "ayr-alert-banner--error",
                "Error Heading",
                "This is an error!",
            ),
            (
                "success",
                "Success Heading",
                "This is a success!",
                "ayr-alert-banner--success",
                "Success Heading",
                "This is a success!",
            ),
        ],
    )
    def test_alert_banner(
        self,
        variant,
        heading,
        message,
        expected_class,
        expected_heading,
        expected_message,
    ):
        """Test the alert_banner macro."""
        rendered = self.macros.alert_banner(
            variant=variant, heading=heading, message=message
        )
        soup = BeautifulSoup(rendered, "html.parser")

        alert_banner = soup.find("div", class_="ayr-alert-banner")
        assert alert_banner is not None
        assert expected_class in alert_banner["class"]

        heading_tag = alert_banner.find(
            "h2", class_="ayr-alert-banner__heading"
        )
        message_tag = alert_banner.find("p", class_="ayr-alert-banner__message")

        assert heading_tag is not None
        assert heading_tag.text == expected_heading

        assert message_tag is not None
        assert message_tag.text == expected_message

    @pytest.mark.parametrize(
        "heading, link_text, link_href, expected_heading, expected_link_text, expected_link_href",
        [
            (
                "Help us to improve this service",
                "Complete our short survey",
                "https://www.smartsurvey.co.uk/s/ayr-feedback/",
                "Help us to improve this service",
                "Complete our short survey",
                "https://www.smartsurvey.co.uk/s/ayr-feedback/",
            ),
            (
                "Belly Band Heading",
                "Click Here",
                "http://example.com",
                "Belly Band Heading",
                "Click Here",
                "http://example.com",
            ),
            (
                "Welcome",
                "Learn More",
                "http://example.org",
                "Welcome",
                "Learn More",
                "http://example.org",
            ),
        ],
    )
    def test_belly_band(
        self,
        heading,
        link_text,
        link_href,
        expected_heading,
        expected_link_text,
        expected_link_href,
    ):
        """Test the belly_band macro."""
        rendered = self.macros.belly_band(
            heading=heading, link_text=link_text, link_href=link_href
        )
        soup = BeautifulSoup(rendered, "html.parser")

        belly_band = soup.find("div", class_="ayr-belly-band")
        assert belly_band is not None

        heading_tag = belly_band.find("h3", class_="govuk-heading-m")
        link_tag = belly_band.find(
            "a", class_="govuk-link govuk-link--no-visited-state"
        )

        assert heading_tag is not None
        assert heading_tag.text == expected_heading

        assert link_tag is not None
        assert link_tag.text == expected_link_text
        assert link_tag["href"] == expected_link_href
