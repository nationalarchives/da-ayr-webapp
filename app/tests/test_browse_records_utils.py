import pytest
from sqlalchemy import event

from app.main.db.models import db
from app.main.util.browse_records_utils import (
    get_autofill_options_rows,
    get_transferring_body_options,
)
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)


@pytest.fixture
def captured_statements(client):
    statements = []

    def record_statement(
        connection, cursor, statement, parameters, context, executemany
    ):
        statements.append(statement)

    engine = db.engine
    event.listen(engine, "before_cursor_execute", record_statement)
    yield statements
    event.remove(engine, "before_cursor_execute", record_statement)


@pytest.mark.parametrize(
    ("accessible_names", "expected"),
    [
        (None, ["empty_body", "populated_body"]),
        (["empty_body"], ["empty_body"]),
        (["populated_body"], ["populated_body"]),
        ([], []),
        (["missing_body"], []),
    ],
)
def test_body_options_do_not_query_files_or_require_hierarchy(
    client, captured_statements, accessible_names, expected
):
    BodyFactory(Name="empty_body")
    BodyFactory(Name="empty_body")
    BodyFactory(Name="")
    BodyFactory(Name=None)
    body = BodyFactory(Name="populated_body")
    FileFactory(consignment=ConsignmentFactory(series=SeriesFactory(body=body)))
    db.session.flush()
    captured_statements.clear()

    assert get_transferring_body_options(accessible_names) == expected
    assert len(captured_statements) == 1
    assert '"File"' not in captured_statements[0]
    assert '"Consignment"' not in captured_statements[0]
    assert '"Series"' not in captured_statements[0]


@pytest.mark.parametrize("filter_by", ["series", "consignment"])
def test_autofill_uses_exists_without_expanding_file_rows(
    client, captured_statements, filter_by
):
    consignment = ConsignmentFactory()
    for _ in range(3):
        FileFactory(consignment=consignment, FileType="fIlE")
    db.session.flush()
    series = consignment.series
    body_name = series.body.Name
    series_name = series.Name
    reference = consignment.ConsignmentReference
    selected_series = series_name.upper() if filter_by == "series" else ""
    selected_consignment = (
        reference.upper() if filter_by == "consignment" else ""
    )
    captured_statements.clear()

    rows = get_autofill_options_rows(
        None, selected_series, selected_consignment
    )

    assert [tuple(row) for row in rows] == [(body_name, series_name, reference)]
    assert len(captured_statements) == 1
    assert "EXISTS (SELECT" in captured_statements[0]
    assert 'JOIN "File"' not in captured_statements[0]


@pytest.mark.parametrize("file_type", [None, "Folder"])
def test_autofill_excludes_consignments_without_eligible_files(
    client, file_type
):
    consignment = ConsignmentFactory()
    if file_type is not None:
        FileFactory(consignment=consignment, FileType=file_type)
    db.session.flush()

    assert get_autofill_options_rows(None, consignment.series.Name, "") == []
    assert (
        get_autofill_options_rows(None, "", consignment.ConsignmentReference)
        == []
    )


@pytest.mark.parametrize("accessible_names", [[], ["other_body"]])
def test_autofill_preserves_body_permissions(client, accessible_names):
    file = FileFactory()
    db.session.flush()

    assert (
        get_autofill_options_rows(
            accessible_names, file.consignment.series.Name, ""
        )
        == []
    )


def test_autofill_exists_is_correlated_to_each_consignment(client):
    populated = ConsignmentFactory()
    empty = ConsignmentFactory(series=populated.series)
    FileFactory(consignment=populated)
    db.session.flush()

    rows = get_autofill_options_rows(
        [populated.series.body.Name], populated.series.Name, ""
    )

    assert [row.consignment_reference for row in rows] == [
        populated.ConsignmentReference
    ]
    assert get_autofill_options_rows(None, "", empty.ConsignmentReference) == []
