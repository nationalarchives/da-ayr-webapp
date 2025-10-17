def validate_page_parameter(value, default=1, min_value=1, max_value=1000):
    """
    Validates and returns a safe integer for pagination parameters.
    Returns default if value is None.
    Aborts with 400 if invalid.
    """
    if value is None:
        return default
    try:
        page = int(value)
        if not (min_value <= page <= max_value):
            return default
        return page
    except (ValueError, TypeError):
        return default
