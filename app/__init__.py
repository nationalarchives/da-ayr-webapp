import inspect
from datetime import datetime

import bleach
from flask import Flask, g
from flask_compress import Compress
from flask_s3 import FlaskS3
from flask_talisman import Talisman
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from app.logger_config import setup_logging
from app.main.db.models import db
from app.main.util.search_utils import OPENSEARCH_FIELD_NAME_MAP
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig

compress = Compress()
talisman = Talisman()
s3 = FlaskS3()


def null_to_dash(value):
    """Filter that converts string values that are "null" or Nones to dash"""
    if value == "null":
        return "-"
    if value is None:
        return "-"
    return value


def clean_tags_and_replace_highlight_tag(text, highlight_tag):
    """Sanitizes ALL HTML tags that are not the highlight tag UUID and replaces them with <mark>"""
    allowed_tags = [highlight_tag]
    clean_text = bleach.clean(text, tags=allowed_tags)
    return clean_text.replace(highlight_tag, "mark")


def format_opensearch_field_name(field):
    """Format the name of an OpenSearch field using a map"""
    return OPENSEARCH_FIELD_NAME_MAP[field]["display_name"]


def format_number_with_commas(number):
    """
    Formats a given number with commas as thousand separators.
    """
    return f"{number:,}"


def format_date_iso(value):
    """Convert 'DD/MM/YYYY' to 'YYYY-MM-DD' if input is a string."""
    if not isinstance(value, str):
        return value

    try:
        date_obj = datetime.strptime(value, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return value


def create_app(config_class, database_uri=None):
    app = Flask(__name__, static_url_path="/assets")
    config = config_class()
    inspect.getmembers(config)
    app.config.from_object(config)

    force_https = False if app.config["TESTING"] else True

    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.filters["null_to_dash"] = null_to_dash
    app.jinja_env.filters["clean_tags_and_replace_highlight_tag"] = (
        clean_tags_and_replace_highlight_tag
    )
    app.jinja_env.filters["format_opensearch_field_name"] = (
        format_opensearch_field_name
    )
    app.jinja_env.filters["format_number_with_commas"] = (
        format_number_with_commas
    )
    app.jinja_env.filters["format_date_iso"] = format_date_iso
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader(
                        "govuk_frontend_jinja"
                    ),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    def get_csp_config(app):
        return {
            "default-src": app.config["CSP_DEFAULT_SRC"],
            "connect-src": app.config["CSP_CONNECT_SRC"],
            "script-src": app.config["CSP_SCRIPT_SRC"],
            "script-src-elem": app.config["CSP_SCRIPT_SRC_ELEM"],
            "style-src": app.config["CSP_STYLE_SRC"],
            "style-src-elem": app.config["CSP_STYLE_SRC_ELEM"],
            "img-src": app.config["CSP_IMG_SRC"],
            "frame-src": app.config["CSP_FRAME_SRC"],
            "object-src": app.config["CSP_OBJECT_SRC"],
            "worker-src": app.config["CSP_WORKER_SRC"],
        }

    csp = get_csp_config(app)

    # setup database uri for testing
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    # Initialise app extensions
    setup_logging(app)
    db.init_app(app)

    def init_extensions(app):

        secrets = AWSSecretsManagerConfig()

        @event.listens_for(db.engine, "handle_error")
        def handle_db_errors(exception_context):
            error = exception_context.original_exception
            if (
                isinstance(error, OperationalError)
                and "password" in str(error).lower()
            ):
                secrets.refresh_db_secret()
                db.engine.dispose()
                return None

        return secrets

    s3.init_app(app)
    compress.init_app(app)
    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=force_https,
        content_security_policy_nonce_in=[
            "script-src-elem",
        ],
    )
    WTFormsHelpers(app)

    # setup database components
    with app.app_context():
        # create db objects for testing else use existing database objects
        if database_uri:
            db.create_all()
        else:
            db.Model.metadata.reflect(bind=db.engine, schema="public")

    # Register blueprints
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_authenticated_view_status():
        """
        This context processor is designed to provide information about the authentication
        status of the current view to the templates.
        It specifically checks if the `access_token_sign_in_required` attribute is set on
        the Flask `g` object, indicating whether the current view requires authentication.

        The `access_token_sign_in_required` attribute is typically set by the
        `access_token_sign_in_required` decorator applied to specific routes. This decorator
        is responsible for enforcing access token sign in requirements and protecting routes
        that require authentication.

        The primary purpose of this context processor is to make the `authenticated_view`
        variable available in templates, allowing template logic to conditionally display
        elements based on whether the current view requires authentication or not.

        Example Usage in a Template:
        ```html
        {% if authenticated_view %}
            <!-- Display elements for authenticated views -->
            <div>
                You are signed in.
            </div>
        {% else %}
            <!-- Display elements for views that do not require authentication -->
            <div>
                Please sign in to access this page.
            </div>
        {% endif %}
        ```

        Note: Ensure that the `access_token_sign_in_required` decorator is appropriately
        applied to routes where authentication is required for accurate behavior of
        this context processor.


        Returns:
            dict: A dictionary containing the `authenticated_view` variable, which is a
                boolean indicating whether the current view requires authentication.
        """
        authenticated_view = getattr(g, "access_token_sign_in_required", False)
        return dict(authenticated_view=authenticated_view)

    @app.after_request
    def add_no_caching_headers(r):
        """
        Add headers to tell browsers not to cache the pages to protected routes
        """
        if g.get("access_token_sign_in_required"):
            r.headers["Cache-Control"] = (
                "public, max-age=0, no-cache, no-store, must-revalidate"
            )
            r.headers["Pragma"] = "no-cache"
            r.headers["Expires"] = "0"
        return r

    return app
