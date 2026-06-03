import json
from pathlib import Path
from unittest.mock import patch

import jwt
from flask import url_for


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_sign_in(mock_keycloak, client):
    mock_keycloak.return_value.auth_url.return_value = "keycloak_auth_url"

    response = client.get("/sign-in")

    assert response.status_code == 302
    assert response.headers["Location"] == "keycloak_auth_url"

    mock_keycloak.return_value.auth_url.assert_called_once_with(
        redirect_uri="http://localhost/callback",
        scope="group_mapper_client_scope",
    )


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_route_all_access_user(mock_keycloak, client):
    mock_keycloak.return_value.token.return_value = {
        "access_token": "valid_access_token",
        "refresh_token": "valid_refresh_token",
    }
    mock_keycloak.return_value.introspect.return_value = {
        "groups": ["/ayr_user_type/view_all"],
        "sub": "test_all_access_user",
    }

    with client.session_transaction() as sess:
        sess["access_token"] = "valid_access_token"
        sess["refresh_token"] = "valid_refresh_token"

    response = client.get("/callback?code=valid_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.browse")

    with client.session_transaction() as sess:
        assert "user_type" in sess
        assert sess["user_type"] == "all_access_user"
        assert sess["user_id"] == "test_all_access_user"


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_route_standard_user(mock_keycloak, client):
    mock_keycloak.return_value.token.return_value = {
        "access_token": "valid_access_token",
        "refresh_token": "valid_refresh_token",
    }
    mock_keycloak.return_value.introspect.return_value = {
        "groups": ["/ayr_user_type/view_dept"],
        "sub": "test_standard_user",
    }

    with client.session_transaction() as sess:
        sess["access_token"] = "valid_access_token"
        sess["refresh_token"] = "valid_refresh_token"

    response = client.get("/callback?code=valid_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.browse")

    with client.session_transaction() as sess:
        assert "user_type" in sess
        assert sess["user_type"] == "standard_user"


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_falls_back_to_userinfo_when_introspect_groups_missing(
    mock_keycloak, client
):
    mock_keycloak.return_value.token.return_value = {
        "access_token": "valid_access_token",
        "refresh_token": "valid_refresh_token",
    }
    mock_keycloak.return_value.introspect.return_value = {
        "sub": "test_all_access_user",
    }
    mock_keycloak.return_value.userinfo.return_value = {
        "groups": ["/ayr_user_type/view_all"],
    }

    response = client.get("/callback?code=valid_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.browse")

    with client.session_transaction() as sess:
        assert sess["user_groups"] == ["/ayr_user_type/view_all"]
        assert sess["user_type"] == "all_access_user"
        assert sess["user_id"] == "test_all_access_user"


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_falls_back_to_access_token_claims_when_userinfo_unavailable(
    mock_keycloak, client
):
    access_token = jwt.encode(
        {
            "sub": "test_all_access_user",
            "groups": ["/ayr_user_type/view_all"],
        },
        key="test-key",
        algorithm="HS256",
    )
    mock_keycloak.return_value.token.return_value = {
        "access_token": access_token,
        "refresh_token": "valid_refresh_token",
    }
    mock_keycloak.return_value.introspect.return_value = {}
    mock_keycloak.return_value.userinfo.side_effect = Exception(
        "userinfo not available"
    )

    response = client.get("/callback?code=valid_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.browse")

    with client.session_transaction() as sess:
        assert sess["user_groups"] == ["/ayr_user_type/view_all"]
        assert sess["user_type"] == "all_access_user"
        assert sess["user_id"] == "test_all_access_user"


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_missing_code(mock_keycloak, client):
    response = client.get("/callback")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.sign_in")


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_invalid_access_token(mock_keycloak, client):
    mock_keycloak_instance = mock_keycloak.return_value

    mock_keycloak_instance.token.return_value = {
        "refresh_token": "refresh_token",
    }

    mock_keycloak_instance.introspect.return_value = {"active": False}

    response = client.get("/callback?code=some_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.sign_in")


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_introspect_invalid_response(mock_keycloak, client):
    mock_keycloak.return_value.token.return_value = {
        "access_token": "some_access_token",
        "refresh_token": "some_refresh_token",
    }

    mock_keycloak.return_value.introspect.side_effect = Exception(
        "Introspection failed"
    )

    response = client.get("/callback?code=some_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.sign_in")


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_callback_tokens_have_expected_keycloak_lifetimes(
    mock_keycloak, client
):
    """
    Given the callback route receives Keycloak access and refresh tokens
    When those tokens are stored in the session
    Then their exp and iat claims should match the Keycloak realm lifetimes
    """
    realm_config_path = (
        Path(__file__).resolve().parents[2]
        / "local_services"
        / "import"
        / "realm-export.json"
    )
    with realm_config_path.open(encoding="utf-8") as realm_config_file:
        realm_config = json.load(realm_config_file)

    access_lifetime = realm_config["accessTokenLifespan"]
    refresh_lifetime = realm_config["ssoSessionIdleTimeout"]

    iat = 1_700_000_000
    mock_keycloak.return_value.token.return_value = {
        "access_token": jwt.encode(
            {"iat": iat, "exp": iat + access_lifetime},
            key="test-key",
            algorithm="HS256",
        ),
        "refresh_token": jwt.encode(
            {"iat": iat, "exp": iat + refresh_lifetime},
            key="test-key",
            algorithm="HS256",
        ),
    }
    mock_keycloak.return_value.introspect.return_value = {
        "groups": ["/ayr_user_type/view_all"],
        "sub": "test_all_access_user",
    }

    response = client.get("/callback?code=valid_code")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.browse")

    with client.session_transaction() as sess:
        access_token = jwt.decode(
            sess["access_token"], options={"verify_signature": False}
        )
        refresh_token = jwt.decode(
            sess["refresh_token"], options={"verify_signature": False}
        )

    assert access_token["exp"] - access_token["iat"] == access_lifetime
    assert refresh_token["exp"] - refresh_token["iat"] == refresh_lifetime
