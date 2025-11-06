from flask import Flask
from marshmallow import Schema, fields

from app.main.util.request_validation_utils import validate_request


class DummySchema(Schema):
    field = fields.String(required=True)


def make_app_with_route(location, schema_class=DummySchema, data=None):
    """Helper to create Flask app and test client for request validation."""
    app = Flask(__name__)

    @app.route("/test", methods=["GET", "POST"])
    @validate_request(schema_class, location=location)
    def test_route(**kwargs):
        return "ok"

    client = app.test_client()
    if location == "args":
        resp = client.get("/test", query_string=data or {"field": "value"})
    elif location == "form":
        resp = client.post("/test", data=data or {"field": "value"})
    elif location == "json":
        resp = client.post("/test", json=data or {"field": "value"})
    elif location == "path":
        # Flask path params need a real route, skip direct test
        return None
    elif location == "combined":
        resp = client.post("/test?field=value", data=data or {"field": "value"})
    else:
        resp = client.get("/test")
    return resp


def test_validate_request_args():
    resp = make_app_with_route("args")
    assert resp.status_code == 200


def test_validate_request_form():
    resp = make_app_with_route("form")
    assert resp.status_code == 200


def test_validate_request_json():
    resp = make_app_with_route("json")
    assert resp.status_code == 200


def test_validate_request_combined():
    resp = make_app_with_route("combined")
    assert resp.status_code == 200


def test_validate_request_invalid_request():
    resp = make_app_with_route("unknown", data={})
    assert resp.status_code == 400
    assert b"Invalid request parameters" in resp.data
