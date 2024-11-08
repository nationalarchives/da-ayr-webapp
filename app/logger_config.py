import logging

from flask import has_request_context, request
from flask.logging import default_handler


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def setup_logging(app):
    formatter = RequestFormatter(
        "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )

    # APP LOGGER
    app_logger = logging.getLogger("app_logger")
    app_handler = logging.StreamHandler()
    app_handler.setFormatter(formatter)
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(app_handler)

    # AUDIT LOGGER
    audit_logger = logging.getLogger("audit_logger")
    audit_handler = logging.StreamHandler()
    audit_handler.setFormatter(formatter)
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)

    app.logger.removeHandler(default_handler)

    app.audit_logger = audit_logger
    app.app_logger = app_logger
