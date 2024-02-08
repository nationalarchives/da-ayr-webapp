import uuid

import boto3
from flask import (
    Response,
    current_app,
    flash,
    json,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from app.main import bp
from app.main.authorize.access_token_sign_in_required import (
    access_token_sign_in_required,
)
from app.main.authorize.ayr_user import AYRUser
from app.main.authorize.permissions_helpers import (
    validate_body_user_groups_or_404,
)
from app.main.db.models import Body, File
from app.main.db.queries import (
    browse_data,
    build_fuzzy_search_query,
    get_all_transferring_bodies,
    get_breadcrumb_values,
    get_file_metadata,
)
from app.main.flask_config_helpers import (
    get_keycloak_instance_from_flask_config,
)
from app.main.forms import CookiesForm
from app.main.util.filter_sort_builder import (
    build_filters,
    build_sorting_orders,
)

from .forms import SearchForm


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/sign-out", methods=["GET"])
@access_token_sign_in_required
def sign_out():
    keycloak_openid = get_keycloak_instance_from_flask_config()
    keycloak_openid.logout(session["refresh_token"])
    session.clear()

    return redirect("/signed-out")


@bp.route("/sign-in", methods=["GET"])
def sign_in():
    keycloak_openid = get_keycloak_instance_from_flask_config()
    auth_url = keycloak_openid.auth_url(
        redirect_uri=f"{request.url_root}callback",
        scope="email",
        state="your_state_info",
    )

    return redirect(auth_url)


@bp.route("/callback", methods=["GET"])
def callback():
    keycloak_openid = get_keycloak_instance_from_flask_config()
    code = request.args.get("code")
    access_token_response = keycloak_openid.token(
        grant_type="authorization_code",
        code=code,
        redirect_uri=f"{request.url_root}callback",
    )

    session["access_token"] = access_token_response["access_token"]
    session["refresh_token"] = access_token_response["refresh_token"]

    return redirect(url_for("main.browse"))


@bp.route("/accessibility", methods=["GET"])
def accessibility():
    return render_template("accessibility.html")


@bp.route("/browse", methods=["POST", "GET"])
@access_token_sign_in_required
def browse():
    transferring_bodies = []
    ayr_user = AYRUser(session.get("user_groups"))
    if ayr_user.is_superuser:
        transferring_bodies = get_all_transferring_bodies()

    form = SearchForm()
    page = int(request.args.get("page", 1))
    per_page = int(current_app.config["DEFAULT_PAGE_SIZE"])

    transferring_body_id = request.args.get("transferring_body_id", None)
    series_id = request.args.get("series_id", None)
    consignment_id = request.args.get("consignment_id", None)

    browse_type = "browse"
    browse_parameters = {}
    filters = {}
    sorting_orders = {}
    breadcrumb_values = {}

    if browse_type == "browse":
        if request.args:
            filters = build_filters(request.args)
            sorting_orders = build_sorting_orders(request.args)

    if transferring_body_id:
        browse_type = "transferring_body"
        browse_parameters["transferring_body_id"] = transferring_body_id
        breadcrumb_values = get_breadcrumb_values(
            transferring_body_id=transferring_body_id
        )
        if request.args:
            filters = build_filters(request.args)
            sorting_orders = build_sorting_orders(request.args)

    elif series_id:
        browse_type = "series"
        browse_parameters["series_id"] = series_id
        breadcrumb_values = get_breadcrumb_values(series_id=series_id)
        if request.args:
            filters = build_filters(request.args)
            sorting_orders = build_sorting_orders(request.args)

    elif consignment_id:
        browse_type = "consignment"
        browse_parameters["consignment_id"] = consignment_id
        breadcrumb_values = get_breadcrumb_values(consignment_id=consignment_id)
        sorting_orders = build_sorting_orders(request.args)

        # e.g. please use example below to pass filter values
        # filters["record_status"] = "open"
        # filters["file_type"] = "docx"
        # filters["date_range"] = {"date_from": "01/08/2022", "date_to": "31/08/2022"}
        # filters["date_filter_field"] = "date_last_modified"
        # e.g. please usd example below to pass sorting order
        # sorting_orders["file_name"] = "asc"  # A to Z
        # sorting_orders["file_name"] = "desc"  # Z to A
        # sorting_orders["record_status"] = "asc"  # A to Z
        # sorting_orders["record_status"] = "desc"  # Z to A
        # sorting_orders["date_last_modified"] = "asc"  # oldest first
        # sorting_orders["date_last_modified"] = "desc"  # most recent first
    else:
        ayr_user = AYRUser(session.get("user_groups"))
        if ayr_user.is_standard_user:
            return redirect(
                f"/browse?transferring_body_id={ayr_user.transferring_body.BodyId}"
            )

    browse_results = browse_data(
        page=page,
        per_page=per_page,
        browse_type=browse_type,
        filters=filters,
        sorting_orders=sorting_orders,
        **browse_parameters,
    )

    num_records_found = browse_results.total

    return render_template(
        "browse.html",
        form=form,
        current_page=page,
        filters=browse_parameters,
        browse_type=browse_type,
        results=browse_results,
        transferring_bodies=transferring_bodies,
        breadcrumb_values=breadcrumb_values,
        user_filters=filters,
        sorting_orders=sorting_orders,
        num_records_found=num_records_found,
    )


@bp.route("/search", methods=["POST", "GET"])
@access_token_sign_in_required
def search():
    form = SearchForm()
    search_results = None
    per_page = int(current_app.config["DEFAULT_PAGE_SIZE"])
    num_records_found = 0
    query = (
        request.form.get("query", "").lower()
        or request.args.get("query", "").lower()
    )
    page = int(request.args.get("page", 1))
    filters = {"query": query}

    if query:
        fuzzy_search_query = build_fuzzy_search_query(query)
        ayr_user = AYRUser(session.get("user_groups"))
        if ayr_user.is_standard_user:
            fuzzy_search_query = fuzzy_search_query.where(
                Body.Name == ayr_user.transferring_body.Name
            )
        search_results = fuzzy_search_query.paginate(
            page=page, per_page=per_page
        )
        num_records_found = search_results.total

    return render_template(
        "search.html",
        form=form,
        current_page=page,
        filters=filters,
        results=search_results,
        num_records_found=num_records_found,
    )


@bp.route("/record/<uuid:record_id>", methods=["GET"])
@access_token_sign_in_required
def record(record_id: uuid.UUID):
    """
    Render the record details page.

    This function retrieves search results from the session, looks for a specific
    record based on the 'record_id' provided in the query parameters, and renders
    the record details on the 'record.html' template.

    Returns:
        A rendered HTML page with record details.
    """
    file = File.query.get_or_404(record_id)

    validate_body_user_groups_or_404(file.consignment.series.body.Name)

    file_metadata = get_file_metadata(record_id)

    return render_template("record.html", record=file_metadata)


@bp.route("/download/<uuid:record_id>")
@access_token_sign_in_required
def download_record(record_id: uuid.UUID):
    file = File.query.get_or_404(record_id)

    validate_body_user_groups_or_404(file.consignment.series.body.Name)

    s3 = boto3.client("s3")
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    file_metadata = get_file_metadata(record_id)
    consignment_reference = file_metadata["consignment"]
    file_path = file_metadata["file_path"]
    key = f'{consignment_reference}/{file_path.rstrip("/")}'
    file_name = file_metadata["file_name"]
    file = s3.get_object(Bucket=bucket, Key=key)

    response = Response(
        file["Body"].read(),
        headers={"Content-Disposition": "attachment;filename=" + file_name},
    )

    return response


@bp.route("/signed-out", methods=["GET"])
def signed_out():
    return render_template("signed-out.html")


@bp.route("/cookies", methods=["GET", "POST"])
def cookies():
    form = CookiesForm()
    # Default cookies policy to reject all categories of cookie
    cookies_policy = {"functional": "no", "analytics": "no"}

    if form.validate_on_submit():
        # Update cookies policy consent from form data
        cookies_policy["functional"] = form.functional.data
        cookies_policy["analytics"] = form.analytics.data

        # Create flash message confirmation before rendering template
        flash("You’ve set your cookie preferences.", "success")

        # Create the response so we can set the cookie before returning
        response = make_response(render_template("cookies.html", form=form))

        # Set cookies policy for one year
        response.set_cookie(
            "cookies_policy", json.dumps(cookies_policy), max_age=31557600
        )
        return response
    elif request.method == "GET":
        if request.cookies.get("cookies_policy"):
            # Set cookie consent radios to current consent
            cookies_policy = json.loads(request.cookies.get("cookies_policy"))
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
        else:
            # If conset not previously set, use default "no" policy
            form.functional.data = cookies_policy["functional"]
            form.analytics.data = cookies_policy["analytics"]
    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html")


@bp.route("/how-to-use-this-service", methods=["GET"])
def how_to_use():
    return render_template("how-to-use-this-service.html")


@bp.route("/terms-of-use", methods=["GET"])
def terms_of_use():
    return render_template("terms-of-use.html")


@bp.app_errorhandler(HTTPException)
def http_exception(error):
    return render_template(f"{error.code}.html"), error.code


@bp.app_errorhandler(CSRFError)
def csrf_error(error):
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.full_path)
