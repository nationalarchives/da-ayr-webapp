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
                "output": "alert-banner.html",
                "context": {
                    "heading": "Default alert banner",
                    "message": "This is the default alert banner.",
                },
            },
            {
                "name": "error",
                "output": "alert-banner-error.html",
                "context": {
                    "variant": "error",
                    "heading": "Error alert banner",
                    "message": "This is the error alert banner.",
                },
            },
            {
                "name": "success",
                "output": "alert-banner-success.html",
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
        "output": "belly-band.html",
        "context": {
            "heading": "Need more help?",
            "link_text": "Contact support",
            "link_href": "https://support.example.com",
        },
    },
    {
        "template": "buttons.html",
        "macro": "govuk_button",
        "output": "govuk-button.html",
        "context": {
            "text": "Rendered button",
            "classes": "extra-class",
        },
    },
]


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
        template = env.get_template(task["template"])
        macro_func = getattr(template.module, task["macro"])

        if "variants" in task:
            for variant in task["variants"]:
                rendered = macro_func(**variant["context"])
                output_path = os.path.join(OUTPUT_DIR, variant.get("output"))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(rendered)
                variant_name = variant.get("name", "default")
                label = f"{task['macro']} ({variant_name})"
                print(f"Rendered {label} → {output_path}")
        else:
            rendered = macro_func(**task["context"])
            output_path = os.path.join(OUTPUT_DIR, task["output"])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(rendered)
            print(f"Rendered {task['macro']} → {output_path}")


if __name__ == "__main__":
    render_macros()
