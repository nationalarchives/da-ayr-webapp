from unittest.mock import patch

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
