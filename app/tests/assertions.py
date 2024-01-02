from bs4 import BeautifulSoup


def assert_contains_html(
    expected_html_subset, html, sub_element_type, sub_element_filter={}
):
    soup = BeautifulSoup(html, "html.parser")
    subset_soup = soup.find(sub_element_type, sub_element_filter)

    expected_subset_soup = BeautifulSoup(expected_html_subset, "html.parser")

    assert expected_subset_soup.prettify() == subset_soup.prettify()  # nosec
