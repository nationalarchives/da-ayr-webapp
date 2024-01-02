from datetime import datetime

from flask import current_app


def get_date_range(date_range):
    date_from = None
    date_to = None
    try:
        if date_range is not None:
            if "date_from" in date_range:
                dt_from = datetime.strptime(
                    str(date_range["date_from"]), "%d/%m/%Y"
                )
                date_from = dt_from.strftime("%Y-%m-%d")
    except ValueError:
        current_app.logger.error(
            "Invalid [date from] value being passed in date range"
        )

    try:
        if date_range is not None:
            if "date_to" in date_range:
                dt_to = datetime.strptime(
                    str(date_range["date_to"]), "%d/%m/%Y"
                )
                date_to = dt_to.strftime("%Y-%m-%d")
    except ValueError:
        current_app.logger.error(
            "Invalid [date to] value being passed in date range"
        )

    return {"date_from": date_from, "date_to": date_to}
