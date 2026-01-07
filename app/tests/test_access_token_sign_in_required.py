from unittest.mock import patch

import keycloak
import pytest
from flask import Flask, render_template, url_for

from app.main.authorize.access_token_sign_in_required import (
    access_token_sign_in_required,
)


class TestAccessTokenSignInRequiredDecorator:
    @staticmethod
    @pytest.mark.parametrize(
        "session_dict",
        [{}, {"access_token": "foo"}, {"refresh_token": "foo"}],
    )
    def test_no_access_or_refresh_token_is_redirected_to_sign_in(
        app, session_dict
    ):
        """
        Given either no access or refresh token in the session,
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should clear the session and redirect to the sign in view
        """
        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            with client.session_transaction() as session:
                session.update(session_dict)

            response = client.get(view_name)

            assert response.status_code == 302
            assert response.headers["Location"] == url_for("main.sign_in")
            with client.session_transaction() as cleared_session:
                assert cleared_session == {}

    @staticmethod
    @patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )
    def test_an_inactive_access_token_and_an_inactive_refresh_token_is_redirected_to_sign_in(
        mock_keycloak, app
    ):
        """
        Given an inactive access token and an inactive refresh token in the session
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should clear the session and redirect to the sign in view
        """
        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            with client.session_transaction() as session:
                session["access_token"] = "inactive_access_token"
                session["refresh_token"] = "inactive_refresh_token"

            session

            def mock_refresh_token(token):
                raise keycloak.exceptions.KeycloakPostError

            mock_keycloak.return_value.refresh_token.side_effect = (
                mock_refresh_token
            )

            def mock_introspect(token):
                if token == "inactive_access_token":
                    return {"active": False}
                elif token == "active_access_token":
                    return {"active": True, "groups": ["a", "b"]}

            mock_keycloak.return_value.introspect.side_effect = mock_introspect

            response = client.get(view_name)

            assert response.status_code == 302
            assert response.headers["Location"] == url_for("main.sign_in")
            with client.session_transaction() as cleared_session:
                assert cleared_session == {}

    @staticmethod
    @patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )
    def test_an_active_access_token_without_ayr_access_is_redirected_to_sign_in(
        mock_keycloak,
        app,
    ):
        """
        Given an active access token in the session,
        And the user does not have access to AYR,
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should redirect to the index page with a flashed message
        """
        app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True

        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            groups = ["a", "b"]

            with client.session_transaction() as session:
                session["access_token"] = "active_access_token"
                session["refresh_token"] = "active_refresh_token"
                session["user_groups"] = groups

            mock_keycloak.return_value.introspect.return_value = {
                "active": True,
                "groups": groups,
            }

            response = client.get(view_name)

            assert response.status_code == 302
            assert response.headers["Location"] == url_for("main.index")

            with client.session_transaction() as session:
                flashed_messages = session["_flashes"]

            assert flashed_messages == [
                (
                    "message",
                    "TNA User is logged in but does not have access to AYR. Please contact your admin.",
                )
            ]

    @staticmethod
    @patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )
    def test_an_inactive_access_token_but_an_active_refresh_token_without_ayr_access_is_redirected_to_index(
        mock_keycloak, app
    ):
        """
        Given an inactive access token and an active refresh token in the session
            that results in an active access token without access to ayr
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should update the session with the
            refreshed access_token, user_groups and refresh_token
        And redirect to the index page with a flashed message
        """
        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            with client.session_transaction() as session:
                session["access_token"] = "inactive_access_token"
                session["refresh_token"] = "active_refresh_token"

            mock_keycloak.return_value.refresh_token.return_value = {
                "access_token": "active_access_token",
                "refresh_token": "new_active_refresh_token",
            }

            def mock_introspect(token):
                if token == "inactive_access_token":
                    return {"active": False}
                elif token == "active_access_token":
                    return {"active": True, "groups": ["a", "b"]}

            mock_keycloak.return_value.introspect.side_effect = mock_introspect

            response = client.get(view_name)

            assert response.status_code == 302
            assert response.headers["Location"] == url_for("main.index")

            with client.session_transaction() as session:
                flashed_messages = session["_flashes"]

            assert flashed_messages == [
                (
                    "message",
                    "TNA User is logged in but does not have access to AYR. Please contact your admin.",
                )
            ]

    @staticmethod
    @patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )
    def test_an_inactive_access_token_but_an_active_refresh_token_with_ayr_access_is_refreshed_and_permitted(
        mock_keycloak, app
    ):
        """
        Given an inactive access token and an active refresh token in the session
            that results in an active access token with access to ayr
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should update the session with the
            refreshed access_token, user_groups and refresh_token
        And grant access
        """
        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            with client.session_transaction() as session:
                session["access_token"] = "inactive_access_token"
                session["refresh_token"] = "active_refresh_token"
                session["user_type"] = "standard_user"

            valid_groups = [
                "/ayr_user_type/view_all",
                "/transferring_body_user/foo",
            ]

            def mock_introspect(token):
                if token == "inactive_access_token":
                    return {"active": False}
                elif token == "active_access_token":
                    return {"active": True, "groups": valid_groups}

            mock_keycloak.return_value.introspect.side_effect = mock_introspect

            mock_keycloak.return_value.refresh_token.return_value = {
                "access_token": "active_access_token",
                "refresh_token": "new_active_refresh_token",
            }

            response = client.get(view_name)

            assert response.status_code == 200
            assert response.data.decode() == "Access granted"

            with client.session_transaction() as updated_session:
                assert updated_session["access_token"] == "active_access_token"
                assert (
                    updated_session["refresh_token"]
                    == "new_active_refresh_token"
                )
                assert updated_session["user_groups"] == valid_groups
                assert updated_session["user_type"] == "all_access_user"

    @staticmethod
    @patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )
    def test_an_active_access_token_with_ayr_access_is_permitted(
        mock_keycloak,
        app,
    ):
        """
        Given an active access token in the session,
        And the user has access to AYR,
        When accessing a route protected by the 'access_token_sign_in_required' decorator,
        Then it should grant access
        """
        view_name = "/protected_view"
        with app.test_client() as client:

            @app.route(view_name)
            @access_token_sign_in_required
            def protected_view():
                return "Access granted"

            valid_groups = [
                "/ayr_user_type/view_dept",
                "/transferring_body_user/foo",
            ]

            with client.session_transaction() as session:
                session["access_token"] = "active_access_token"
                session["refresh_token"] = "active_refresh_token"
                session["user_groups"] = valid_groups

            mock_keycloak.return_value.introspect.return_value = {
                "active": True,
                "groups": valid_groups,
            }

            response = client.get(view_name)

        assert response.status_code == 200
        assert response.data.decode() == "Access granted"


def test_expected_unprotected_routes_decorated_by_access_token_sign_in_required(
    app,
):
    """
    Given a Flask application created by create_app,
    When checking which routes are protected or unprotected by the 'access_token_sign_in_required' decorator,
    Then the protected routes should match the expected protected routes,
    And the unprotected routes should match the expected unprotected routes.
    """
    expected_protected_routes = [
        "main.search",
        "main.search_results_summary",
        "main.search_transferring_body",
        "main.record",
        "main.download_record",
        "main.sign_out",
        "main.browse",
        "main.browse_transferring_body",
        "main.browse_series",
        "main.browse_consignment",
        "main.generate_manifest",
        "main.get_page_image",
        "main.get_page_thumbnail",
    ]
    expected_unprotected_routes = [
        "static",
        "main.index",
        "main.sign_in",
        "main.signed_out",
        "main.callback",
        "main.accessibility",
        "main.cookies",
        "main.privacy",
        "main.how_to_use",
        "main.terms_of_use",
    ]

    (
        protected_routes,
        unprotected_routes,
    ) = get_expected_routes_separated_by_protection(app)

    assert set(protected_routes) == set(expected_protected_routes)
    assert set(unprotected_routes) == set(expected_unprotected_routes)


def get_expected_routes_separated_by_protection(app) -> tuple[list, list]:
    """
    Retrieve the routes of a Flask application separated by 'access_token_sign_in_required' protection.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        tuple[list, list]: A tuple containing two lists.
            - The first list includes the names of routes protected by 'access_token_sign_in_required' decorator.
            - The second list includes the names of routes without the 'access_token_sign_in_required' decorator.
    """
    protected_routes = []
    unprotected_routes = []
    with app.app_context():
        for view_function_name, view_function in app.view_functions.items():
            if (
                getattr(view_function, "access_token_sign_in_required", False)
                is True
            ):
                protected_routes.append(view_function_name)
            else:
                unprotected_routes.append(view_function_name)
    return protected_routes, unprotected_routes


def test_get_expected_routes_separated_by_protection():
    """
    Given a basic Flask application with routes and views,
    When calling the get_expected_routes_separated_by_protection function,
    Then the returned protected routes should match the routes with the 'access_token_sign_in_required' decorator
    And the returned unprotected routes should match the routes without the 'access_token_sign_in_required' decorator
    """
    app = Flask(__name__)

    @app.route("/protected")
    @access_token_sign_in_required
    def protected_view():
        return "Protected View"

    @app.route("/unprotected")
    def unprotected_view():
        return "Unprotected View"

    @app.route("/another_protected")
    @access_token_sign_in_required
    def another_protected_view():
        return "Another Protected View"

    (
        protected_routes,
        unprotected_routes,
    ) = get_expected_routes_separated_by_protection(app)

    assert set(protected_routes) == {"protected_view", "another_protected_view"}
    assert set(unprotected_routes) == {"static", "unprotected_view"}


def test_sign_out_button_on_protected_view_that_uses_base_template(
    app, mock_standard_user
):
    """
    Given a view that is protected by the 'access_token_sign_in_required' decorator,
        and renders the `base.html` template
    When an authenticated user accesses the view,
    Then the response should contain a 'Sign out' button.
    """
    view_name = "/extended_base_view"

    @app.route(view_name)
    @access_token_sign_in_required
    def protected_base_view():
        return render_template(
            "base.html",
        )

    with app.test_client() as client:
        mock_standard_user(client)
        response = client.get(view_name)

    assert response.status_code == 200
    assert "Sign out" in response.data.decode()


def test_no_sign_out_button_on_unprotected_view_that_uses_base_template(app):
    """
    Given a view that is NOT protected by the 'access_token_sign_in_required' decorator,
        and renders the `base.html` template
    When a user accesses the view,
    Then the response should not contain a 'Sign out' button.
    """
    view_name = "/extended_base_view"

    @app.route(view_name)
    def unprotected_base_view():
        return render_template(
            "base.html",
        )

    with app.test_client() as client:
        response = client.get(view_name)

    assert response.status_code == 200
    assert "Sign out" not in response.data.decode()


def test_no_cache_headers_not_set_on_response_for_unprotected_view(app):
    """
    Given a view that is NOT protected by the 'access_token_sign_in_required' decorator,
    When a user accesses the view,
    Then the response headers should not contain
        "Expires", "Pragma" or "Cache-Control" entries
    """
    view_name = "/unprotected_view"

    @app.route(view_name)
    def unprotected_base_view():
        return "Unprotected View"

    with app.test_client() as client:
        response = client.get(view_name)

    assert all(
        key not in response.headers
        for key in ["Expires", "Pragma", "Cache-Control"]
    )
