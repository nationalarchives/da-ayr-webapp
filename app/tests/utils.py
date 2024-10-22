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
    List[List[str]], e.g. [["row_1_value_1", "row_1_value_2"], ["row_2_value_1", "row_2_value_2"]]
    """
    rows = table.find_all("tr")
    data = []
    for row in rows:
        row_data = []
        cells = row.find_all("td")
        for cell in cells:
            for tag in cell.find_all(True):
                if tag.name != "mark":
                    tag.unwrap()
            cell_value = cell.decode_contents(formatter="html").strip()
            if cell_value:
                row_data.append(cell_value)
        if row_data:
            data.append(row_data)
    return data


def get_table_rows_header_values(table):
    """
    Returns all header values as a list of strings
    :param table: BeautifulSoup object
    Returns:
    List[str], e.g. ["value1", "value2"]
    """
    headers = table.find_all("th")
    return [header.get_text(strip=True) for header in headers]
