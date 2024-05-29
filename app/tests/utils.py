def decompose_desktop_invisible_elements(soup):
    """
    this function removes html elements with class 'govuk-table--invisible-on-desktop' from a BeautifulSoup object
    :param soup: BeautifulSoup
    """
    for invisible_element in soup.find_all(
        attrs={"class": "govuk-table--invisible-on-desktop"}
    ):
        invisible_element.decompose()


def decompose_mobile_invisible_elements(soup):
    """
    this function removes html elements with class 'govuk-table--invisible-on-mobile' from a BeautifulSoup object
    :param soup: BeautifulSoup
    """
    for invisible_element in soup.find_all(
        attrs={"class": "govuk-table--invisible-on-mobile"}
    ):
        invisible_element.decompose()
