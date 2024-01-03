from app.main.util.date_formatter import get_date_range


def test_browse_data_date_from_filter_exception_raised(app, caplog):
    """
    Given an invalid date_from value
    When get_date_range function is called
    Then it returns and empty date range and logs an error message
    """
    dt_range = {"date_from": "junk"}
    results = get_date_range(date_range=dt_range)
    assert "Invalid [date from] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}


def test_browse_data_date_to_filter_exception_raised(app, caplog):
    """
    Given an invalid date_to value
    When get_date_range function is called
    Then it returns and empty date range and logs an error message
    """
    dt_range = {"date_to": "junk"}
    results = get_date_range(date_range=dt_range)
    assert "Invalid [date to] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}


def test_browse_data_date_from_and_to_filter_exception_raised(app, caplog):
    """
    Given an invalid date_from and date_to value
    When get_date_range function is called
    Then it returns and empty date range and logs an error message
    """
    dt_range = {"date_from": "junk", "date_to": "junk"}
    results = get_date_range(date_range=dt_range)
    assert "Invalid [date from] value being passed in date range" in caplog.text
    assert "Invalid [date to] value being passed in date range" in caplog.text
    assert results == {"date_from": None, "date_to": None}
