import logging
import os

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


def setup_logging(app):
    formatter = RequestFormatter(
        "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )

    app_logger = logging.getLogger("app_logger")
    app_logger.setLevel(logging.INFO)
    audit_logger = logging.getLogger("audit_logger")
    audit_logger.setLevel(logging.INFO)

    if os.getenv("CONFIG_SOURCE") == "AWS_SECRETS_MANAGER":
        environment_name = os.getenv("ENVIRONMENT_NAME")
        log_group_name = f"ayr-test-one-app-logs"
        app_handler = CloudWatchHandler(
            log_group=log_group_name, stream_name="app-log-stream"
        )
        audit_handler = CloudWatchHandler(
            log_group=log_group_name, stream_name="audit-log-stream"
        )
    else:
        app_handler = logging.StreamHandler()
        audit_handler = logging.StreamHandler()

    app_handler.setFormatter(formatter)
    audit_handler.setFormatter(formatter)

    app_logger.addHandler(app_handler)
    audit_logger.addHandler(audit_handler)

    app.audit_logger = audit_logger
    app.app_logger = app_logger
