from app.main.db.queries import get_default_start_date
from app.main.util.date_validator import (
    generate_default_date_values,
    get_date,
    validate_dates,
)


def build_filters(args):
    filters = {}
    if args:
        filter_items = []
        transferring_body = args.get("transferring_body_filter", "").lower()

        if transferring_body and transferring_body != "all":
            filter_items.append({"transferring_body": transferring_body})

        series = args.get("series_filter", "").lower()
        if series:
            filter_items.append({"series": series})

        _build_date_range_filter(args, filter_items)

        for f in filter_items:
            for key, value in f.items():
                filters[key] = value

    return filters


def build_sorting_orders(args):
    sorting_orders = {}
    if args:
        if args.get("sort"):
            sort_details = args.get("sort").split("-")
            sort_by = None
            sort_order = None
            if len(sort_details) > 1:
                sort_by = sort_details[0].strip()
                sort_order = sort_details[1].strip()

            if sort_by and sort_order:
                sorting_orders[sort_by] = sort_order

    return sorting_orders


def build_browse_consignment_filters(args):
    filters = {}
    if args:
        filter_items = []
        record_status = args.get("record_status")
        date_filter_field = args.get("date_filter_field")

        if record_status:
            filter_items.append({"record_status": record_status})
        if date_filter_field:
            filter_items.append({"date_filter_field": date_filter_field})

        _build_date_range_filter(args, filter_items, date_filter_field)

        for f in filter_items:
            for key, value in f.items():
                filters[key] = value

    return filters


def _build_date_range_filter(args, filter_items, date_filter_field=None):
    date_validation_errors = validate_dates(args)

    if len(date_validation_errors) == 0:
        default_start_date = get_default_start_date(date_filter_field)
        date_inputs = generate_default_date_values(args, default_start_date)
    else:
        dt_from = get_date(
            args.get("date_from_day"),
            args.get("date_from_month"),
            args.get("date_from_year"),
            "#",
        )
        date_from = f"{dt_from[0]}/{dt_from[1]}/{dt_from[2]}"

        dt_to = get_date(
            args.get("date_to_day"),
            args.get("date_to_month"),
            args.get("date_to_year"),
            "#",
        )
        date_to = f"{dt_to[0]}/{dt_to[1]}/{dt_to[2]}"

        date_inputs = {"date_from": date_from, "date_to": date_to}

    dt_from = None
    dt_to = None
    if date_inputs["date_from"]:
        dt_from = date_inputs["date_from"].replace("#", "") != "//"
    if date_inputs["date_to"]:
        dt_to = date_inputs["date_to"].replace("#", "") != "//"

    if dt_from and dt_to:
        filter_items.append(
            {
                "date_range": {
                    "date_from": date_inputs["date_from"],
                    "date_to": date_inputs["date_to"],
                }
            }
        )
    elif dt_from:
        filter_items.append(
            {"date_range": {"date_from": date_inputs["date_from"]}}
        )
    elif dt_to:
        filter_items.append({"date_range": {"date_to": date_inputs["date_to"]}})
