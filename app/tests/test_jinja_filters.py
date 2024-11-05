import pytest

from app import clean_tags, null_to_dash


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        # input is string "null"
        ("null", "-"),
        # input is None
        (None, "-"),
        # input is an empty string
        ("", ""),
        # input is an integer zero
        (0, 0),
        # input is a string zero
        ("0", "0"),
        # input is a non-zero integer
        (123, 123),
        # input is just a string and not "null"
        ("hello", "hello"),
        # input is a more complex type
        (["null", None], ["null", None]),
        # input is a boolean False
        (False, False),
        # input is a boolean True
        (True, True),
    ],
)
def test_null_to_dash(input_value, expected_output):
    assert null_to_dash(input_value) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        # input with non-mark HTML tags
        ("<div>Test</div> <span>Text</span>", "Test Text"),
        # input with ALLOWED <mark> tag
        ("<mark>Highlight</mark>", "<mark>Highlight</mark>"),
        # mixed tags with <mark> and other tags
        ("<mark>Keep</mark> <div>Remove</div>", "<mark>Keep</mark> Remove"),
        # nested tags including <mark>
        ("<div><mark>Inside</mark> Div</div>", "<mark>Inside</mark> Div"),
        # self-closing tag (e.g., <img>)
        ("<img src='image.png'/>Picture", "Picture"),
        # no tags in input
        ("Just plain text", "Just plain text"),
        # tags with attributes
        ("<p class='text'>Paragraph</p>", "Paragraph"),
        # mixed case-sensitive tags (e.g., <Mark> vs <mark>)
        ("<Mark>Upper</Mark> <mark>Lower</mark>", "Upper <mark>Lower</mark>"),
        # empty tag pairs
        ("<div></div>", ""),
        # unclosed tag
        ("<span>Open tag", "Open tag"),
        # EXTREMELY IMPORTANT: removed stript tags (even if we have CSP)
        ("<script>This is a script tag</script>", "This is a script tag"),
        # EXTREMELY IMPORTANT: self closing script tags
        (
            "<script/>This is a self closing script tag",
            "This is a self closing script tag",
        ),
        # EXTREMELY IMPORTANT: script tags with attributes
        (
            "<script src='myscript.js'>This is a script tag with attrs</script>",
            "This is a script tag with attrs",
        ),
    ],
)
def test_clean_tags(input_text, expected_output):
    assert clean_tags(input_text) == expected_output
