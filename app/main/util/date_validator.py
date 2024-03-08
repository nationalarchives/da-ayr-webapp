from datetime import date, datetime

from flask import current_app

db_date_format = "%Y-%m-%d"
python_date_format = "%d/%m/%Y"
default_start_date = None
check_future_date = True


def validate_date_range(date_range):
    date_from = None
    date_to = None
    if date_range is not None:
        if "date_from" in date_range:
            try:
                dt_from = datetime.strptime(
                    str(date_range["date_from"]), python_date_format
                )
                date_from = dt_from.strftime(db_date_format)
            except ValueError:
                current_app.logger.error(
                    "Invalid [date from] value being passed in date range"
                )

        if "date_to" in date_range:
            try:
                dt_to = datetime.strptime(
                    str(date_range["date_to"]), python_date_format
                )
                date_to = dt_to.strftime(db_date_format)
            except ValueError:
                current_app.logger.error(
                    "Invalid [date to] value being passed in date range"
                )

    return {"date_from": date_from, "date_to": date_to}


def get_date(day, month, year, value):
    day_var = (
        day.rjust(2, "0") if len(str(day)) == 1 else day if day else value * 2
    )
    month_var = (
        month.rjust(2, "0")
        if len(str(month)) == 1
        else month if month else value * 2
    )
    year_var = year.ljust(4, "0") if year and len(str(year)) > 0 else value * 4

    return [day_var, month_var, year_var]


def generate_date_values(args):
    date_from = get_date(
        args.get("date_from_day"),
        args.get("date_from_month"),
        args.get("date_from_year"),
        "0",
    )

    date_values = {
        "1": date_from[0],
        "2": date_from[1],
        "3": date_from[2],
    }

    date_to = get_date(
        args.get("date_to_day"),
        args.get("date_to_month"),
        args.get("date_to_year"),
        "0",
    )
    date_values.update(
        {
            "4": date_to[0],
            "5": date_to[1],
            "6": date_to[2],
        }
    )

    return date_values


def generate_default_date_values(args, start_date=None):
    global default_start_date
    default_start_date = start_date if start_date else default_start_date

    date_values = generate_date_values(args)
    date_values = {key: int(val) for key, val in date_values.items()}

    if all(value == 0 for value in date_values.values()):
        return {"date_from": "##/##/####", "date_to": "##/##/####"}

    date_from = _create_date(
        date_values["3"], date_values["2"], date_values["1"]
    )
    date_to = _create_date(date_values["6"], date_values["5"], date_values["4"])

    if date_from and date_to:
        return {
            "date_from": date_from.strftime(python_date_format),
            "date_to": date_to.strftime(python_date_format),
        }

    if date_values["2"] > 0 and date_values["3"] > 0:
        dates = _get_default_date(date_values["2"], date_values["3"], "to_date")
        return {
            "date_from": dates["from_date"],
            "date_to": dates["to_date"],
        }

    if date_values["5"] > 0 and date_values["6"] > 0:
        dates = _get_default_date(
            date_values["5"], date_values["6"], "from_date"
        )

        return {
            "date_from": dates["from_date"],
            "date_to": dates["to_date"],
        }

    dates = _get_dates_based_on_year(date_values)

    if dates:
        return {"date_from": dates["date_from"], "date_to": dates["date_to"]}


def validate_dates(args, validate_future_date=True):
    global check_future_date
    check_future_date = (
        validate_future_date if validate_future_date else check_future_date
    )

    date_values = generate_date_values(args)
    date_from_set = [
        value for key, value in date_values.items() if key in "1,2,3"
    ]
    date_to_set = [
        value for key, value in date_values.items() if key in "4,5,6"
    ]

    errors = {}

    if not all(value.isdigit() for value in date_from_set):
        errors = {"date_from": "‘Date from’ must be a real date"}

    if not all(value.isdigit() for value in date_to_set):
        if len(errors) > 0:
            errors.update({"date_to": "‘Date to’ must be a real date"})
        else:
            errors = {"date_to": "‘Date to’ must be a real date"}
    if errors:
        return errors

    date_values = {key: int(val) for key, val in date_values.items()}

    date_from_errs = _validate_date(
        date_values["1"],
        date_values["2"],
        date_values["3"],
        "date_from",
        "‘Date from’",
    )
    date_to_errs = _validate_date(
        date_values["4"],
        date_values["5"],
        date_values["6"],
        "date_to",
        "‘Date to’",
    )

    if len(date_from_errs) == 0 and len(date_to_errs) == 0:

        date_from = _create_date(
            date_values["3"], date_values["2"], date_values["1"]
        )
        date_to = _create_date(
            date_values["6"], date_values["5"], date_values["4"]
        )

        if date_from and date_to:
            if date_from > date_to:
                err = date_to.strftime(python_date_format)
                err_str = f"‘Date from’ must be the same as or before ‘{err}’"
                errors = {"date_from": err_str}
    else:
        errors.update(date_from_errs)
        errors.update(date_to_errs)

    return errors


def _validate_date(
    day,
    month,
    year,
    key,
    value,
):
    errors = {}
    if (year == 0 and day > 0 and month > 0) or (
        day == 0 and year == 0 and month > 0
    ):
        errors = {key: f"{value} must include a year"}
    if (month == 0 and day > 0 and year > 0) or (
        day > 0 and month == 0 and year == 0
    ):
        errors = {key: f"{value} must include a month"}
    if month > 0 and not _valid_month(month):
        errors = {key: f"{value} must be a real date"}
    elif day > 0 and month > 0 and year > 0:
        if not _valid_day(day, month, year):
            errors = {key: f"{value} must be a real date"}

        if len(errors) == 0:
            input_date = date(year, month, day)
            if input_date > date.today() and check_future_date:
                errors = {key: f"{value} must be in the past"}

    return errors


def _valid_day(day, month, year):
    last_day = _get_last_day_of_month(month, year)

    if day < 1 or day > last_day:
        return False
    else:
        return True


def _valid_month(month):
    if month < 1 or month > 12:
        return False
    else:
        return True


def _get_dates_based_on_year(date_values):
    date_from = None
    date_to = None
    set1 = [value for key, value in date_values.items() if key not in "3"]
    set2 = [value for key, value in date_values.items() if key not in "6"]
    set3 = [
        value for key, value in date_values.items() if key not in ("3", "6")
    ]

    if date_values["3"] > 0 and all(value == 0 for value in set1):
        dates = _get_default_day_and_month(date_values["3"], None)
        date_from = dates["from_date"]
        date_to = dates["to_date"]

    if date_values["6"] > 0 and all(value == 0 for value in set2):
        dates = _get_default_day_and_month(None, date_values["6"])
        date_from = dates["from_date"]
        date_to = dates["to_date"]

    if (
        date_values["3"] > 0
        and date_values["6"] > 0
        and all(value == 0 for value in set3)
    ):
        dates = _get_default_day_and_month(date_values["3"], date_values["6"])
        date_from = dates["from_date"]
        date_to = dates["to_date"]

    return {"date_from": date_from, "date_to": date_to}


def _get_last_day_of_month(month, year):
    if month == 2:
        if year % 4 == 0 or year % 100 == 0 or year % 400 == 0:
            last_day = 29
        else:
            last_day = 28
    elif month in (1, 3, 5, 7, 8, 10, 12):
        last_day = 31
    else:
        last_day = 30

    return last_day


def _get_default_day_and_month(date_from_year, date_to_year):
    from_date = None
    year = None
    if date_from_year and date_to_year:
        from_date = date(date_from_year, 1, 1)
        year = date_to_year
    elif date_from_year:
        from_date = date(date_from_year, 1, 1)
        year = date_from_year
    elif date_to_year:
        from_date = default_start_date
        year = date_to_year

    if year == datetime.now().year:
        to_date = date.today()
    else:
        to_date = date(year, 12, 31)

    return {
        "from_date": from_date.strftime(python_date_format),
        "to_date": to_date.strftime(python_date_format),
    }


def _get_default_date(month, year, date_to_set):
    from_date = None
    to_date = None

    last_day = _get_last_day_of_month(month, year)

    # check current month
    if check_future_date:
        if year == datetime.now().year and month == datetime.now().month:
            last_day = datetime.now().day

    if month and year and date_to_set == "to_date":
        from_date = date(year, month, 1)
        to_date = date.today()
    elif month and year and date_to_set == "from_date":
        from_date = default_start_date
        to_date = date(year, month, last_day)

    return {
        "from_date": (
            from_date.strftime(python_date_format) if from_date else from_date
        ),
        "to_date": (
            to_date.strftime(python_date_format) if to_date else to_date
        ),
    }


def _create_date(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        return None
