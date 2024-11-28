import logging

import boto3
from botocore.exceptions import ClientError
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


class CloudWatchHandler(logging.Handler):
    def __init__(self, log_group, stream_name):
        super().__init__()
        self.client = boto3.client("logs")
        self.log_group = log_group
        self.stream_name = stream_name

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.stream_name,
                logEvents=[
                    {
                        "timestamp": int(record.created * 1000),
                        "message": log_entry,
                    }
                ],
            )
        except ClientError as e:
            print(f"Error sending log to CloudWatch: {e}")


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
