import uuid

import keycloak
from flask import (
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
from app.main.db.queries import browse_data, fuzzy_search, get_file_metadata
from app.main.forms import CookiesForm

from .forms import SearchForm


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/sign-out", methods=["GET"])
@access_token_sign_in_required
def sign_out():
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )
    keycloak_openid.logout(session["refresh_token"])
    session.clear()

    return redirect("/signed-out")


@bp.route("/sign-in", methods=["GET"])
def sign_in():
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )
    auth_url = keycloak_openid.auth_url(
        redirect_uri=f"{request.url_root}callback",
        scope="email",
        state="your_state_info",
    )

    return redirect(auth_url)


@bp.route("/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )
    access_token_response = keycloak_openid.token(
        grant_type="authorization_code",
        code=code,
        redirect_uri=f"{request.url_root}callback",
    )

    session["access_token_response"] = access_token_response
    session["access_token"] = access_token_response["access_token"]
    session["refresh_token"] = access_token_response["refresh_token"]
    session["token_type"] = access_token_response["token_type"]
    session["token_scope"] = access_token_response["scope"]
    session["session_state"] = access_token_response["session_state"]

    return redirect(url_for("main.browse"))


@bp.route("/accessibility", methods=["GET"])
def accessibility():
    return render_template("accessibility.html")


@bp.route("/browse", methods=["POST", "GET"])
@access_token_sign_in_required
def browse():
    form = SearchForm()
    page = int(request.args.get("page", 1))
    per_page = int(current_app.config["DEFAULT_PAGE_SIZE"])

    transferring_body_id = request.args.get("transferring_body_id", None)
    series_id = request.args.get("series_id", None)
    consignment_id = request.args.get("consignment_id", None)

    browse_type = "browse"

    if transferring_body_id:
        browse_type = "transferring_body"
        filters = {"transferring_body_id": transferring_body_id}
    elif series_id:
        browse_type = "series"
        filters = {"series_id": series_id}
    elif consignment_id:
        browse_type = "consignment"
        filters = {"consignment_id": consignment_id}
    else:
        filters = {}

    browse_results = browse_data(page=page, per_page=per_page, **filters)

    num_records_found = browse_results.total

    return render_template(
        "browse.html",
        form=form,
        current_page=page,
        browse_type=browse_type,
        results=browse_results,
        num_records_found=num_records_found,
    )


@bp.route("/poc-search", methods=["POST", "GET"])
@access_token_sign_in_required
def poc_search():
    form = SearchForm()
    search_results = None
    per_page = int(current_app.config["DEFAULT_PAGE_SIZE"])
    num_records_found = 0
    query = (
        request.form.get("query", "").lower()
        or request.args.get("query", "").lower()
    )
    page = int(request.args.get("page", 1))

    if query:
        search_results = fuzzy_search(query, page, per_page)
        num_records_found = search_results.total

    return render_template(
        "poc-search.html",
        form=form,
        current_page=page,
        query=query,
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
    record_metadata = get_file_metadata(record_id)

    record_dict = {
        "file_name": record_metadata[1],
        "status": record_metadata[2],
        "description": record_metadata[3],
        "date_last_modified": record_metadata[4],
        "held_by": record_metadata[5],
        "legal_status": record_metadata[6],
        "rights_copyright": record_metadata[7],
        "language": record_metadata[8],
        "consignment_id": record_metadata[9],
        "transferring_body": record_metadata[10],
    }

    return render_template("record.html", record=record_dict)


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
