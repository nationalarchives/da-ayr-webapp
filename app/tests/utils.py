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


def evaluate_table_body_rows(soup, expected_results):
    """
    Gets all rows and cell values for a table inside a page after decomposing invisible items then asserts the result
    :param soup: BeautifulSoup
    :param espected_results: string[][]
    """
    decompose_desktop_invisible_elements(soup)
    table_body = soup.find("tbody")
    rows = table_body.find_all("tr")

    data = []

    for row in rows:
        row_data = []
        cells = row.find_all("td")
        for cell in cells:
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)

    return data == expected_results
