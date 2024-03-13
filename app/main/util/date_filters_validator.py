from datetime import date

from app.main.util.date_validator import validate_dates


def validate_date_filters(args, browse_consignment=False):
    from_date = to_date = None
    date_filters = {}

    (
        from_day,
        from_month,
        from_year,
        to_day,
        to_month,
        to_year,
        date_validation_errors,
    ) = validate_dates(args, browse_consignment=browse_consignment)

    if browse_consignment and "date_filter_field" in date_validation_errors:
        return date_validation_errors, from_date, to_date, date_filters

    if not (
        date_validation_errors["date_from"] or date_validation_errors["date_to"]
    ):
        if from_year and from_month and from_day:
            from_date = date(from_year, from_month, from_day)
            from_day, from_month, from_year = _format_date_elements(
                from_day, from_month, from_year
            )
            date_filters = {
                "from_day": from_day,
                "from_month": from_month,
                "from_year": from_year,
            }
        if to_year and to_month and to_day:
            to_date = date(to_year, to_month, to_day)
            to_day, to_month, to_year = _format_date_elements(
                to_day, to_month, to_year
            )
            date_filters.update(
                {"to_day": to_day, "to_month": to_month, "to_year": to_year}
            )
    else:
        if from_year or from_month or from_day:
            from_day, from_month, from_year = _format_date_elements(
                from_day, from_month, from_year
            )
            date_filters = {
                "from_day": from_day,
                "from_month": from_month,
                "from_year": from_year,
            }
        if to_year or to_month or to_day:
            to_day, to_month, to_year = _format_date_elements(
                to_day, to_month, to_year
            )
            date_filters.update(
                {"to_day": to_day, "to_month": to_month, "to_year": to_year}
            )

    return date_validation_errors, from_date, to_date, date_filters


def _format_date_elements(day, month, year):
    day_var = (
        str(day).rjust(2, "0") if len(str(day)) == 1 else day if day else 0 * 2
    )
    month_var = (
        str(month).rjust(2, "0")
        if len(str(month)) == 1
        else month if month else 0 * 2
    )
    year_var = str(year).ljust(4, "0") if year and len(str(year)) > 0 else 0 * 4

    return day_var, month_var, year_var
