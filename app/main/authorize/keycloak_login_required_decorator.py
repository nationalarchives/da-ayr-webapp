from functools import wraps

from flask import redirect, session, url_for

from app.main.authorize.keycloak_manager import is_valid_token_for_ayr


def access_token_login_required():
    def decorator(view_func):
        @wraps(view_func)
        def decorated_view(*args, **kwargs):
            access_token = session.get("access_token")
            if not (access_token and is_valid_token_for_ayr(access_token)):
                return redirect(url_for("main.index"))
            return view_func(*args, **kwargs)

        return decorated_view

    return decorator
