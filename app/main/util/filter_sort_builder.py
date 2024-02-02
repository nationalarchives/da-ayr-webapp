def build_filters(args):
    filter_items = []
    filters = {}
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


def build_sorting_orders_consignment(request):
    sorting_orders = {}
    if not request.args.get("sort"):
        sorting_orders = {"closure_type": "asc"}
    if request.args.get("sort") == "closure_type_asc":
        sorting_orders["closure_type"] = "asc"  # A to Z closed to open
    if request.args.get("sort") == "closure_type_desc":
        sorting_orders["closure_type"] = "desc"  # Z to A open to closed
    if request.args.get("sort") == "filename_asc":
        sorting_orders["file_name"] = "asc"  # A to Z
    if request.args.get("sort") == "filename_desc":
        sorting_orders["file_name"] = "desc"  # Z to A
    if request.args.get("sort") == "last_modified_date_desc":
        sorting_orders["date_last_modified"] = "desc"  # oldest first
    if request.args.get("sort") == "last_modified_date_asc":
        sorting_orders["date_last_modified"] = "asc"  # most recent first
    if request.args.get("sort") == "closure_expiry_date_asc":
        sorting_orders["date_last_modified"] = "desc"

    return sorting_orders


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
