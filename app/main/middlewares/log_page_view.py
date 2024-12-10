import json
from functools import wraps

from flask import current_app, request, session


def log_page_view(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id", "anonymous")
        log_data = {
            "event": "api_request",
            "user_id": user_id,
            "route": request.url,
            "method": request.method,
            "caller_function": route_function.__name__,
            "caller_module": route_function.__module__,
        }
        current_app.audit_logger.info(json.dumps(log_data))
        return route_function(*args, **kwargs)

    return wrapper
