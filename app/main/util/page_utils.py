from flask import (
    current_app,
    redirect,
    request,
    url_for,
)


def get_page_and_per_page(validated_data):
    page = validated_data.get("page")
    per_page = validated_data.get("per_page")
    if not per_page:
        per_page = int(current_app.config["DEFAULT_PAGE_SIZE"])
    return page, per_page


def redirect_if_page_invalid(requested_page, default_page, endpoint, **kwargs):
    """
    Redirects to the default page if the requested page is invalid (e.g., out of range).
    Returns a redirect response if a redirect is needed, otherwise None.
    """
    if int(requested_page) != default_page:
        # Copy current query parameters and set page to default_page
        args = request.args.to_dict()
        args["page"] = default_page
        return redirect(url_for(endpoint, **kwargs, **args))
