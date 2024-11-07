import inspect

import bleach
from flask import Flask, g
from flask_compress import Compress
from flask_s3 import FlaskS3
from flask_talisman import Talisman
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from app.logger_config import setup_logging
from app.main.db.models import db

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


def clean_tags(text, highlight_tag):
    """Sanitizes ALL HTML tags that are not <mark>"""
    allowed_tags = [highlight_tag]
    text = bleach.clean(text, tags=allowed_tags)
    return text.replace(highlight_tag, "mark")


def create_app(config_class, database_uri=None):
    app = Flask(__name__, static_url_path="/assets")
    config = config_class()
    inspect.getmembers(config)
    app.config.from_object(config)

    force_https = False if app.config["TESTING"] else True

    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.filters["null_to_dash"] = null_to_dash
    app.jinja_env.filters["clean_tags"] = clean_tags
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

    SELF = "'self'"

    csp = {
        "default-src": f" {SELF} {app.config['FLASKS3_CDN_DOMAIN']} ",
        "connect-src": [
            SELF,
            app.config["FLASKS3_CDN_DOMAIN"],
            f"https://{app.config['RECORD_BUCKET_NAME']}.s3.amazonaws.com",
        ],
        "script-src": (
            [
                SELF,
                f"{app.config['FLASKS3_CDN_DOMAIN']}",
                f"https://{app.config['RECORD_BUCKET_NAME']}.s3.amazonaws.com",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/5315.4c3c820c7f8b3cc26be6.js",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/998.9c1bd6b181b8236d95c2.js",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/7484.468f27df41f99efd4b79.js",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/2185.34b4770909a62ebe892e.js",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/3171.f31082f3b568ce907389.js",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/umd/4864.b0b319b4f29542847e0e.js",
                "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js",
                "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
                "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",  # pragma: allowlist secret
                "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",  # pragma: allowlist secret
                "'sha256-JTVvglOxxHXAPZcB40r0wZGNZuFHt0cm0bQVn8LK5GQ='",  # pragma: allowlist secret
                "'sha256-LnUrbI34R6DmHbJR754/DQ0b/JKCTdo/+BKs5oLAyNY='",  # pragma: allowlist secret
                "'sha256-74nJjfZHR0MDaNHtes/sgN253tXMCsa4SeniH8bU3x8='",  # pragma: allowlist secret
            ]
        ),
        "style-src": [
            SELF,
            "'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE='",  # pragma: allowlist secret
            "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",  # pragma: allowlist secret
            "'sha256-s6M/FyyCCegtJyBnH26lkxb67XZxuZKosiCQWD+VaSo='",  # pragma: allowlist secret
            "'sha256-gNGYzcxL9BKlQFzUxh3BgvhKn2szEIFgg65uQvfaxiI='",  # pragma: allowlist secret
            "'sha256-jcxDeNpsDPUI+dIIqUyA3VBoLgf3Mi2LkRWL/H61who='",  # pragma: allowlist secret
            "'sha256-crS7z4MA9wqqtYsAtmJ6LiW05hz4QJTaokDTQAzc+Hs='",  # pragma: allowlist secret
            "'sha256-8Vn73Z5msbLVngI0nj0OnoRknDpixmr5Qqxqq1oVeyw='",  # pragma: allowlist secret
            "'sha256-1u1O/sNzLBXqLGKzuRbVTI5abqBQBfKsNv3bH5iXOkg='",  # pragma: allowlist secret
            "'sha256-xDT4BUH+7vjNzOH1DSYRS8mdxJbvLVPYsb8hjk4Yccg='",  # pragma: allowlist secret
            "'sha256-ylK9YBCBEaApMPzc82Ol5H/Hd5kmcv3wQlT3Y5m7Kn4='",  # pragma: allowlist secret
        ],
        "style-src-elem": [
            SELF,
            f"{app.config['FLASKS3_CDN_DOMAIN']}",
            "https://cdn.jsdelivr.net/jsdelivr-header.css",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/uv.min.css",
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/src/css/main.css",
            # ----int instance styles----
            "https://d2tm6k52k7dws9.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://d2tm6k52k7dws9.cloudfront.net/assets/src/css/main.css",
            "'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE='",  # pragma: allowlist secret
            # ---------------------------
            "'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE='",  # pragma: allowlist secret
            "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",  # pragma: allowlist secret
            "'sha256-s6M/FyyCCegtJyBnH26lkxb67XZxuZKosiCQWD+VaSo='",  # pragma: allowlist secret
            "'sha256-gNGYzcxL9BKlQFzUxh3BgvhKn2szEIFgg65uQvfaxiI='",  # pragma: allowlist secret
            "'sha256-jcxDeNpsDPUI+dIIqUyA3VBoLgf3Mi2LkRWL/H61who='",  # pragma: allowlist secret
            "'sha256-crS7z4MA9wqqtYsAtmJ6LiW05hz4QJTaokDTQAzc+Hs='",  # pragma: allowlist secret
            "'sha256-8Vn73Z5msbLVngI0nj0OnoRknDpixmr5Qqxqq1oVeyw='",  # pragma: allowlist secret
            "'sha256-1u1O/sNzLBXqLGKzuRbVTI5abqBQBfKsNv3bH5iXOkg='",  # pragma: allowlist secret
            "'sha256-xDT4BUH+7vjNzOH1DSYRS8mdxJbvLVPYsb8hjk4Yccg='",  # pragma: allowlist secret
        ],
        "worker-src": [
            "blob:",
            SELF,
            f"{app.config['FLASKS3_CDN_DOMAIN']}",
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
            "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",  # pragma: allowlist secret
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",  # pragma: allowlist secret
        ],
        "img-src": (f"'self' {app.config['FLASKS3_CDN_DOMAIN']} data: "),
        "object-src": f"https://{app.config['RECORD_BUCKET_NAME']}.s3.amazonaws.com",
        "frame-src": f"https://{app.config['RECORD_BUCKET_NAME']}.s3.amazonaws.com",
    }

    # setup database uri for testing
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    # Initialise app extensions
    setup_logging(app)
    db.init_app(app)
    s3.init_app(app)
    compress.init_app(app)
    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=force_https,
        content_security_policy_nonce_in=[
            "script-src",
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
