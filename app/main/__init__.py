from flask import Blueprint

from app.main.authorize.keycloak_manager import (
    get_keycloak_openid_object_from_aws_params,
)

keycloak_openid = get_keycloak_openid_object_from_aws_params()
bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401
