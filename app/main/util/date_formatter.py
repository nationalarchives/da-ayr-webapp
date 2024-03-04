from datetime import date, datetime

from flask import current_app


def validate_date_range(date_range):
    date_from = None
    date_to = None
    if date_range is not None:
        if "date_from" in date_range:
            try:
                dt_from = datetime.strptime(
                    str(date_range["date_from"]), "%d/%m/%Y"
                )
                date_from = dt_from.strftime("%Y-%m-%d")
            except ValueError:
                current_app.logger.error(
                    "Invalid [date from] value being passed in date range"
                )

        if "date_to" in date_range:
            try:
                dt_to = datetime.strptime(
                    str(date_range["date_to"]), "%d/%m/%Y"
                )
                date_to = dt_to.strftime("%Y-%m-%d")
            except ValueError:
                current_app.logger.error(
                    "Invalid [date to] value being passed in date range"
                )

    return {"date_from": date_from, "date_to": date_to}


default_date_format = "%d/%m/%Y"


def validate_dates(
    date_from_day,
    date_from_month,
    date_from_year,
    date_to_day,
    date_to_month,
    date_to_year,
):
    date_from_errors = _validate_date(
        date_from_day,
        date_from_month,
        date_from_year,
        "date_from",
        "‘Date from’",
    )
    date_to_errors = _validate_date(
        date_to_day, date_to_month, date_to_year, "date_to", "‘Date to’"
    )

    errors = {}

    if len(date_from_errors) == 0 and len(date_to_errors) == 0:
        from_date = None
        to_date = None

        if (
            len(date_from_day) > 0
            and len(date_from_month) > 0
            and len(date_from_year) > 0
        ):
            from_date = date(
                int(date_from_year), int(date_from_month), int(date_from_day)
            )
        if (
            len(date_to_day) > 0
            and len(date_to_month) > 0
            and len(date_to_year) > 0
        ):
            to_date = date(
                int(date_to_year), int(date_to_month), int(date_to_day)
            )

        if from_date and to_date:
            if from_date > to_date:
                err = to_date.strftime(default_date_format)
                err_str = (
                    f"‘Date from’ must be the same as or before [= ‘{err}’]"
                )
                errors = {"date_from": err_str}
            elif to_date > from_date:
                err = from_date.strftime(default_date_format)
                err_str = f"‘To date’ must be the same as or before [= ‘{err}’]"
                errors = {"date_from": err_str}
    else:
        errors.update(date_from_errors)
        errors.update(date_to_errors)

    return errors


def _validate_date(
    day,
    month,
    year,
    key,
    value,
):
    errors = {}

    if not year and day and month:
        errors = {key: f"{value} must include a year"}
    if not month and day and year:
        errors = {key: f"{value} must include a month"}
    if not (month and year) and day:
        errors = {key: f"{value} must be a real date"}
    elif day.isdigit() and month.isdigit() and year.isdigit():
        if not _validate_day(day, month, year):
            errors = {key: f"{value} must be a real date"}

        if len(errors) == 0:
            input_date = date(int(year), int(month), int(day))
            if input_date > date.today():
                errors = {key: f"{value} must be in the past"}

    return errors


def _validate_day(day, month, year):
    is_valid = True
    if int(month) == 2:
        if int(year) % 4 == 0 or int(year) % 100 == 0 or int(year) % 400 == 0:
            if int(day) < 1 or int(day) > 29:
                is_valid = False
        else:
            if int(day) < 1 or int(day) > 28:
                is_valid = False
    elif int(month) in (1, 3, 5, 7, 8, 10, 12):
        if int(day) < 1 or int(day) > 31:
            is_valid = False
    else:
        if int(day) < 1 or int(day) > 30:
            is_valid = False

    return is_valid


def get_default_day(month, year):
    first_day = 1
    if int(month) == 2:
        if int(year) % 4 == 0 or int(year) % 100 == 0 or int(year) % 400 == 0:
            last_day = 29
        else:
            last_day = 28
    elif int(month) in (1, 3, 5, 7, 8, 10, 12):
        last_day = 31
    else:
        last_day = 30

    return {"first_day": first_day, "last_day": last_day}


def get_default_day_and_month(date_from_year, date_to_year):
    if date_from_year and date_to_year:
        from_date = date(int(date_from_year), 1, 1)
        to_date = date(int(date_to_year), 12, 31)
    elif date_from_year:
        from_date = date(int(date_from_year), 1, 1)
        to_date = datetime.today()
    elif date_to_year:
        from_date = date(1900, 1, 1)
        to_date = date(int(date_to_year), 12, 31)

    return {"from_date": from_date, "to_date": to_date}


def get_default_date(month, year, date_to_set):
    days = get_default_day(int(month), int(year))

    if month and year and date_to_set == "to_date":
        from_date = date(int(year), int(month), days["first_day"])
        to_date = datetime.today()
    elif month and year and date_to_set == "from_date":
        from_date = date(1900, 1, 1)
        to_date = date(int(year), int(month), days["last_day"])

    return {"from_date": from_date, "to_date": to_date}
