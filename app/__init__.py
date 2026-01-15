import inspect
import socket
import sys
import traceback
from datetime import datetime

import bleach
import boto3
import psycopg2
from flask import Flask, g
from flask_compress import Compress
from flask_s3 import FlaskS3
from flask_talisman import Talisman
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

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

    # Initialise extensions
    setup_logging(app)
    db.init_app(app)
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

    with app.app_context():
        if database_uri:
            app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
            db.create_all()

        else:
            cfg = AWSSecretsManagerConfig()
            rds = boto3.client("rds")

            print("\n=== DEBUG: Configuration & Environment ===")
            print(f"Current UTC time:          {datetime.utcnow().isoformat()}")
            print(f"DB_HOST (repr):            {repr(cfg.DB_HOST)}")
            print(f"DB_PORT (repr):            {repr(cfg.DB_PORT)}")
            print(f"DB_USER:                   {cfg.DB_USER}")
            print(f"DB_NAME:                   {cfg.DB_NAME}")
            print(f"AWS_REGION:                {cfg.AWS_REGION}")
            print(f"Python version:            {sys.version.splitlines()[0]}")
            print("Running in:                Lambda / CloudShell / Other")

            def get_connection():
                print("\n--- New connection attempt ---")
                print(
                    f"[{datetime.utcnow().isoformat()}] Using DB_HOST: {repr(cfg.DB_HOST)}"
                )

                # DNS resolution check from inside this runtime
                print("DNS resolution check:")
                try:
                    resolved_ips = socket.gethostbyname_ex(cfg.DB_HOST)[2]
                    print(f"  → Resolves to IPs: {resolved_ips}")
                    print(
                        f"  → First IP: {resolved_ips[0] if resolved_ips else 'None'}"
                    )
                except socket.gaierror as dns_err:
                    print(f"  → DNS resolution FAILED: {dns_err}")
                except Exception as e:
                    print(f"  → DNS check error: {type(e).__name__}: {e}")

                # Token generation
                print(
                    f"[{datetime.utcnow().isoformat()}] Generating IAM auth token for:"
                )
                print(f"  Hostname: {repr(cfg.DB_HOST)}")
                print(f"  Port:     {repr(cfg.DB_PORT)}")
                print(f"  User:     {repr(cfg.DB_USER)}")

                try:
                    token = rds.generate_db_auth_token(
                        DBHostname=cfg.DB_HOST,
                        Port=int(cfg.DB_PORT),
                        DBUsername=cfg.DB_USER,
                        Region=cfg.AWS_REGION,
                    )
                    print("Token generated successfully")
                    print(f"Token length: {len(token)}")
                    print(f"Token prefix (first 120 chars):\n{token[:120]}...")
                    print(
                        f"Expected prefix starts with: {repr(cfg.DB_HOST + ':' + cfg.DB_PORT + '/')}"
                    )

                    # Quick self-check
                    expected_start = f"{cfg.DB_HOST}:{cfg.DB_PORT}/"
                    actual_start = token[: len(expected_start)]
                    print(
                        f"Token matches expected start? {actual_start == expected_start}"
                    )
                    if not actual_start == expected_start:
                        print("!!! TOKEN PREFIX MISMATCH DETECTED !!!")
                except Exception as gen_err:
                    print("!!! TOKEN GENERATION FAILED !!!")
                    print(f"Error: {type(gen_err).__name__}: {gen_err}")
                    traceback.print_exc()
                    raise

                # Connection attempt
                print(
                    f"[{datetime.utcnow().isoformat()}] Attempting psycopg2.connect() with:"
                )
                print(f"  host={repr(cfg.DB_HOST)}")
                print(f"  port={repr(cfg.DB_PORT)}")
                print(f"  user={repr(cfg.DB_USER)}")
                print(f"  dbname={repr(cfg.DB_NAME)}")
                print("  sslmode=require")

                try:
                    conn = psycopg2.connect(
                        host=cfg.DB_HOST,
                        port=int(cfg.DB_PORT),
                        user=cfg.DB_USER,
                        password=token,
                        database=cfg.DB_NAME,
                        sslmode="require",
                        connect_timeout=10,
                    )
                    print("!!! CONNECTION SUCCEEDED !!!")
                    return conn
                except psycopg2.OperationalError as op_err:
                    print(
                        "!!! psycopg2 OperationalError (most likely proxy rejection) !!!"
                    )
                    print(f"Error: {op_err}")
                    print(f"pgcode: {op_err.pgcode}")
                    print(f"pgerror: {op_err.pgerror}")
                    print(f"DB_HOST at failure: {repr(cfg.DB_HOST)}")
                    raise
                except psycopg2.Error as pg_err:
                    print("!!! General psycopg2 Error !!!")
                    print(f"Error: {pg_err}")
                    traceback.print_exc()
                    raise
                except Exception as conn_err:
                    print("!!! Unexpected connection error !!!")
                    print(f"Type: {type(conn_err).__name__}")
                    print(f"Message: {conn_err}")
                    traceback.print_exc()
                    raise

            try:
                print("\nCreating SQLAlchemy engine...")
                engine = create_engine(
                    "postgresql+psycopg2://",
                    creator=get_connection,
                    poolclass=NullPool,
                )
                print("Engine created successfully")
            except Exception as engine_err:
                print("!!! ENGINE CREATION FAILED !!!")
                print(f"Error: {engine_err}")
                traceback.print_exc()
                raise

            db.session.configure(bind=engine)
            app.logger.info("Created DB connection with IAM auth")

            try:
                print("Reflecting metadata...")
                db.Model.metadata.reflect(bind=engine, schema="public")
                print("Metadata reflection succeeded")
            except Exception as reflect_err:
                print("!!! METADATA REFLECTION FAILED !!!")
                print(f"Error: {reflect_err}")
                traceback.print_exc()
                raise

    # Register blueprints
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_authenticated_view_status():
        authenticated_view = getattr(g, "access_token_sign_in_required", False)
        return dict(authenticated_view=authenticated_view)

    @app.after_request
    def add_no_caching_headers(r):
        if g.get("access_token_sign_in_required"):
            r.headers["Cache-Control"] = (
                "public, max-age=0, no-cache, no-store, must-revalidate"
            )
            r.headers["Pragma"] = "no-cache"
            r.headers["Expires"] = "0"
        return r

    return app
