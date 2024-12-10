import inspect
import json
import logging

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "log_type": record.name,
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.module,
            "function": self.get_calling_function_name(record),
            "line_number": record.lineno,
        }

        if has_request_context():
            log_record.update(
                {
                    "remote_addr": request.remote_addr,
                    "url": request.url,
                }
            )

        try:
            message_data = json.loads(record.getMessage())
            if isinstance(message_data, dict):
                log_record.update(message_data)
            else:
                log_record["message"] = message_data
        except json.JSONDecodeError:
            log_record["message"] = record.getMessage()

        return json.dumps(log_record)

    def get_calling_function_name(self, record):
        if record.stack_info:
            stack_frames = inspect.extract_stack(record.stack_info)
            print("STACK FRAMES", stack_frames)
            if len(stack_frames) > 1:
                # The second frame is the calling function
                calling_frame = stack_frames[-2]
                return calling_frame.function
        return None


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
    audit_log_formatter = RequestFormatter()
    app.audit_logger = setup_logger(
        "audit_logger", logging.INFO, audit_log_formatter
    )

    app_log_formatter = RequestFormatter()
    app.app_logger = setup_logger("app_logger", logging.INFO, app_log_formatter)
