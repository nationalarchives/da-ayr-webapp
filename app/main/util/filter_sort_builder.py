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
            _build_date_range_filter(args, filter_items)

        for f in filter_items:
            for key, value in f.items():
                filters[key] = value

    return filters


def _build_date_range_filter(args, filter_items):
    date_from_day = args.get("date_from_day", "")
    date_from_month = args.get("date_from_month", "")
    date_from_year = args.get("date_from_year", "")
    date_from = date_from_day + "/" + date_from_month + "/" + date_from_year
    date_to_day = args.get("date_to_day", "")
    date_to_month = args.get("date_to_month", "")
    date_to_year = args.get("date_to_year", "")
    date_to = date_to_day + "/" + date_to_month + "/" + date_to_year

    if (date_from and date_from != "//") and (date_to and date_to != "//"):
        filter_items.append(
            {"date_range": {"date_from": date_from, "date_to": date_to}}
        )
    elif date_from and date_from != "//":
        filter_items.append({"date_range": {"date_from": date_from}})
    elif date_to and date_to != "//":
        filter_items.append({"date_range": {"date_to": date_to}})
