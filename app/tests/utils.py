def decompose_desktop_invisible_elements(soup):
    """
    this function removes html elements with class 'govuk-table--invisible-on-desktop' from a BeautifulSoup object
    :param soup: BeautifulSoup
    """
    for invisible_element in soup.find_all(
        attrs={"class": "govuk-table--invisible-on-desktop"}
    ):
        invisible_element.decompose()


def decompose_inner_tables(soup):
    """
    this function removes tables with the id 'inner-table' from a BeautifulSoup object
    :param soup: BeautifulSoup
    """
    for element in soup.find_all(attrs={"id": "inner-table"}):
        element.decompose()


def decompose_mobile_invisible_elements(soup):
    """
    this function removes html elements with class 'govuk-table--invisible-on-mobile' from a BeautifulSoup object
    :param soup: BeautifulSoup
    """
    for invisible_element in soup.find_all(
        attrs={"class": "govuk-table--invisible-on-mobile"}
    ):
        invisible_element.decompose()


def get_table_rows_cell_values(table):
    """
    Returns all rows and cell values for a table that has been found using BeautifulSoup
    :param table: BeautifulSoup object
    Returns:
    string[][], e.g. [["row_1_value_1", "row_1_value_2"], ["row_2_value_1", "row_2_value_2"]]
    """
    rows = table.find_all("tr")
    data = []
    for row in rows:
        row_data = []
        cells = row.find_all("td")
        for cell in cells:
            cell_value = cell.get_text(separator=" ", strip=True)
            if len(cell_value) > 1:
                row_data.append(cell_value)
        if len(row_data) > 1:
            data.append(row_data)
    return data
