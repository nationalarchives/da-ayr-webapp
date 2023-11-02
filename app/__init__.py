import os

import boto3
from flask import Flask
from flask_assets import Bundle, Environment
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from config import Config

assets = Environment()
compress = Compress()
csrf = CSRFProtect()
limiter = Limiter(
    get_remote_address, default_limits=["2 per second", "60 per minute"]
)
talisman = Talisman()


def null_to_dash(value):
    if value == "null":
        return "-"
    if value is None:
        return "-"
    return value


# use only for local development
if os.environ.get("DEFAULT_AWS_PROFILE"):
    boto3.setup_default_session(
        profile_name=os.environ.get("DEFAULT_AWS_PROFILE")
    )


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path="/assets")
    app.config.from_object(config_class)

    force_https = False if app.config["TESTING"] else True

    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.filters["null_to_dash"] = null_to_dash
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

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "script-src": ["'self'"],
    }

    # Initialise app extensions
    assets.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=csp, force_https=force_https)
    WTFormsHelpers(app)

    # Create static asset bundles
    css = Bundle(
        "src/css/*.css",
        filters="cssmin",
        output="dist/css/custom-%(version)s.min.css",
    )
    js = Bundle(
        "src/js/*.js",
        filters="jsmin",
        output="dist/js/custom-%(version)s.min.js",
    )
    if "css" not in assets:
        assets.register("css", css)
    if "js" not in assets:
        assets.register("js", js)

    # Register blueprints
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
