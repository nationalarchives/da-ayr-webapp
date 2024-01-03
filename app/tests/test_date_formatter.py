from app.main.util.date_formatter import validate_date_range


def test_logs_message_and_returns_none_date_when_invalid_from_date(app, caplog):
    """
    Given an invalid date_from value
    When validate_date_range function is called
    Then it returns an empty date range and logs error messages
    """
    dt_range = {"date_from": "junk"}
    results = validate_date_range(date_range=dt_range)
    assert "Invalid [date from] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}


def test_logs_message_and_returns_none_date_when_invalid_to_date(app, caplog):
    """
    Given an invalid date_to value
    When validate_date_range function is called
    Then it returns an empty date range and logs error messages
    """
    dt_range = {"date_to": "junk"}
    results = validate_date_range(date_range=dt_range)
    assert "Invalid [date to] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}


def test_logs_messages_and_returns_none_dates_when_invalid_dates(app, caplog):
    """
    Given an invalid date_from and date_to values
    When validate_date_range function is called
    Then it returns an empty date range and logs error messages
    """
    dt_range = {"date_from": "junk", "date_to": "junk"}
    results = validate_date_range(date_range=dt_range)
    assert "Invalid [date from] value being passed in date range" in caplog.text
    assert "Invalid [date to] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}
