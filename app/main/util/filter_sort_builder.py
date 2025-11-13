def build_filters(args, date_from, date_to):
    filters = {}
    filter_items = []
    if args:
        transferring_body = args["transferring_body_filter"]

        if transferring_body and transferring_body != "all":
            filter_items.append({"transferring_body": transferring_body})

        series = args["series_filter"]
        if series:
            filter_items.append({"series": series})

    if date_from or date_to:
        _build_date_range_filter(date_from, date_to, filter_items)

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


def build_browse_consignment_filters(args, date_from, date_to):
    filters = {}
    filter_items = []
    date_filter_field = args.get("date_filter_field")
    if args:
        record_status = args.get("record_status")

        if record_status:
            filter_items.append({"record_status": record_status})
        if date_filter_field:
            filter_items.append({"date_filter_field": date_filter_field})

    if date_from or date_to:
        _build_date_range_filter(date_from, date_to, filter_items)

    for f in filter_items:
        for key, value in f.items():
            filters[key] = value

    return filters


db_date_format = "%Y-%m-%d"


def _build_date_range_filter(date_from, date_to, filter_items):
    filter_items.append(
        {
            "date_from": (
                date_from.strftime(db_date_format) if date_from else None
            ),
            "date_to": date_to.strftime(db_date_format) if date_to else None,
        }
    )
