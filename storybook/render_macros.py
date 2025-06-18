import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = os.path.dirname(__file__)
MACROS_DIR = os.path.join(BASE_DIR, "..", "app", "templates", "main", "macros")
OUTPUT_DIR = os.path.join(BASE_DIR, "html")

# Define macro render tasks.
# Each task can either define:
# - A single variant with "context" and "output", OR
# - Multiple variants using a "variants" list.
MACRO_RENDER_TASKS = [
    {
        "template": "banners.html",
        "macro": "alert_banner",
        "variants": [
            {
                "context": {
                    "heading": "Default alert banner",
                    "message": "This is the default alert banner.",
                },
            },
            {
                "name": "error",
                "context": {
                    "variant": "error",
                    "heading": "Error alert banner",
                    "message": "This is the error alert banner.",
                },
            },
            {
                "name": "success",
                "context": {
                    "variant": "success",
                    "heading": "Success alert banner",
                    "message": "This is the success alert banner.",
                },
            },
        ],
    },
    {
        "template": "banners.html",
        "macro": "belly_band",
        "variants": [
            {
                "context": {
                    "heading": "Need more help?",
                    "link_text": "Contact support",
                    "link_href": "https://support.example.com",
                },
            }
        ],
    },
    {
        "template": "buttons.html",
        "macro": "govuk_button",
        "variants": [
            {
                "context": {
                    "text": "Rendered button",
                    "classes": "extra-class",
                },
            }
        ],
    },
]


def get_output_filename(macro_name, variant_name=None):
    """
    Generates an output filename in kebab-case format for a given macro and optional variant.
    """

    def _to_kebab_case(s):
        return s.replace("_", "-")

    name = f"{_to_kebab_case(macro_name)}{f'-{_to_kebab_case(variant_name)}' if variant_name else ''}.html"
    return name


def render_macros():
    """
    Renders Jinja macros into static HTML files based on predefined tasks.

    Each task specifies:
    - `template`: the Jinja file containing the macro.
    - `macro`: the name of the macro function.
    - EITHER:
        - `context` + `output`: for a single render,
        - OR `variants`: a list of objects each with `context` and `output`.

    Output files are written to the OUTPUT_DIR.
    """
    env = Environment(
        loader=FileSystemLoader(MACROS_DIR),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    )

    for task in MACRO_RENDER_TASKS:
        macro = getattr(
            env.get_template(task["template"]).module, task["macro"]
        )

        for variant in task.get("variants", []):
            name = variant.get("name")
            output_path = os.path.join(
                OUTPUT_DIR, get_output_filename(task["macro"], name)
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w") as f:
                f.write(macro(**variant["context"]))

            label = f"{task['macro']} ({name})" if name else task["macro"]
            print(f"Rendered {label} → {output_path}")


if __name__ == "__main__":
    render_macros()
