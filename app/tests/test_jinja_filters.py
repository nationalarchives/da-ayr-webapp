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
        (
            "<div>Test</div> <span>Text</span>",
            "&lt;div&gt;Test&lt;/div&gt; &lt;span&gt;Text&lt;/span&gt;",
        ),
        # input with ALLOWED <mark> tag
        ("<mark>Highlight</mark>", "<mark>Highlight</mark>"),
        # mixed tags with <mark> and other tags
        (
            "<mark>Keep</mark> <div>Remove</div>",
            "<mark>Keep</mark> &lt;div&gt;Remove&lt;/div&gt;",
        ),
        # nested tags including <mark>
        (
            "<div><mark>Inside</mark> Div</div>",
            "&lt;div&gt;<mark>Inside</mark> Div&lt;/div&gt;",
        ),
        # self-closing tag (e.g., <img>)
        (
            "<img src='image.png'/>Picture",
            "&lt;img src='image.png'/&gt;Picture",
        ),
        # no tags in input
        ("Just plain text", "Just plain text"),
        # tags with attributes
        (
            "<p class='text'>Paragraph</p>",
            "&lt;p class='text'&gt;Paragraph&lt;/p&gt;",
        ),
        # mixed case-sensitive tags (e.g., <Mark> vs <mark>) - HTML tags are not case sensitive
        (
            "<Mark>Upper</Mark> <mark>Lower</mark>",
            "<mark>Upper</mark> <mark>Lower</mark>",
        ),
        # empty tag pairs
        ("<div></div>", "&lt;div&gt;&lt;/div&gt;"),
        # unclosed tag
        ("<span>Open tag", "&lt;span&gt;Open tag"),
        # EXTREMELY IMPORTANT: removed stript tags (even if we have CSP)
        (
            "<script>This is a script tag</script>",
            "&lt;script&gt;This is a script tag&lt;/script&gt;",
        ),
        # EXTREMELY IMPORTANT: self closing script tags
        (
            "<script/>This is a self closing script tag",
            "&lt;script/&gt;This is a self closing script tag",
        ),
        # EXTREMELY IMPORTANT: script tags with attributes
        (
            "<script src='myscript.js'>This is a script tag with attrs</script>",
            "&lt;script src='myscript.js'&gt;This is a script tag with attrs&lt;/script&gt;",
        ),
    ],
)
def test_clean_tags(input_text, expected_output):
    assert clean_tags(input_text) == expected_output
