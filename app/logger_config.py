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
    default_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
