def build_sorting_orders(request):
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
