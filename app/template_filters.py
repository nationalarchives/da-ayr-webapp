import datetime


def format_datetime(value: str) -> str:
    """
    Converts a string representation of a datetime in the format "%Y-%m-%dT%H:%M:%S"
    to a formatted date string in the format "%d/%m/%Y".

    Parameters:
    - value (str): A string representing a datetime in the format "%Y-%m-%dT%H:%M:%S".

    Returns:
    - str: A formatted date string in the format "%d/%m/%Y".

    If the input string is not in the expected format or if a ValueError or TypeError
    occurs during the conversion, the function returns a hyphen ("-").
    """
    try:
        datetime_object = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return "-"

    return datetime_object.strftime("%d/%m/%Y")
