from bs4 import BeautifulSoup


def assert_contains_html(
    expected_html_subset, html, sub_element_type, sub_element_filter={}
):
    expected_soup = BeautifulSoup(expected_html_subset, "html.parser")
    expected_element = expected_soup.find(sub_element_type)

    if expected_element is None:
        raise ValueError(
            f"Invalid test setup: expected_html_subset must contain a {sub_element_type} element."
        )

    soup = BeautifulSoup(html, "html.parser")
    actual_element = soup.find(sub_element_type, sub_element_filter)

    assert (
        actual_element is not None
    ), f"Element not found: {sub_element_type} with filter {sub_element_filter}"  # nosec

    # normalise both elements by converting to a string representation
    # This handles attribute ordering differences
    def normalise_element(element):
        """Convert element to a normalised dictionary for comparison"""
        return {
            "tag": element.name,
            "attrs": sorted(element.attrs.items()),
            "text": element.get_text(strip=True),
            "children": [
                normalise_element(child)
                for child in element.children
                if child.name
            ],
        }

    expected_normalised = normalise_element(expected_element)
    actual_normalised = normalise_element(actual_element)

    assert expected_normalised == actual_normalised  # nosec
