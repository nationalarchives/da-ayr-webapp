import logging

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)


def setup_logger(name, level, formatter):
    """Helper function to set up a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def setup_logging(app):
    """Set up loggers for the app."""
    audit_log_formatter = RequestFormatter(
        "AUDIT_LOG\n"
        "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )
    app.audit_logger = setup_logger(
        "audit_logger", logging.INFO, audit_log_formatter
    )

    app_log_formatter = RequestFormatter(
        "APP_LOG\n"
        "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )
    app.app_logger = setup_logger("app_logger", logging.INFO, app_log_formatter)
