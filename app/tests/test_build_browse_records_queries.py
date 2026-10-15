from datetime import datetime

import pytest
from bs4 import BeautifulSoup
from sqlalchemy import func
from sqlalchemy.dialects import postgresql

from app.main.db.models import Consignment, File, Series, db
from app.main.db.queries import (
    build_browse_records_base_query,
    build_browse_records_queries,
)
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)

SORT_FIELDS = ["date_of_record", "opening_date", "file_name", "series"]


@pytest.fixture
def records(client):
    body = BodyFactory(Name="permitted")
    files = []
    # Duplicate series names and an empty series must not lose eligible files.
    SeriesFactory(body=body, Name="empty")
    for group, name in enumerate(["alpha", "alpha", "omega", None]):
        series = SeriesFactory(body=body, Name=name)
        for batch in range(2):
            consignment = ConsignmentFactory(series=series)
            for item in range(6):
                number = group * 12 + batch * 6 + item
                date = datetime(2020, 1, number % 28 + 1, number % 24)
                files.append(
                    FileFactory(
                        consignment=consignment,
                        FileName=f"record-{number:03d}",
                        FileType="Folder" if item == 0 else "FILE",
                        ClosureType=["Open", "Closed", "Retained for security"][
                            item % 3
                        ],
                        EndDate=date if item % 2 and item != 5 else None,
                        DateLastModified=date if item != 5 else None,
                        OpeningDate=date if item != 4 else None,
                    )
                )
    FileFactory(
        consignment=ConsignmentFactory(
            series=SeriesFactory(
                body=BodyFactory(Name="denied"), Name="aardvark"
            )
        ),
        FileName="unauthorized",
        EndDate=datetime(1900, 1, 1),
    )
    db.session.flush()
    return files


def sort_values(rows, field):
    columns = {
        "date_of_record": func.coalesce(File.EndDate, File.DateLastModified),
        "opening_date": File.OpeningDate,
        "file_name": File.FileName,
        "series": Series.Name,
    }
    values = dict(
        db.session.query(File.FileId, columns[field])
        .join(File.consignment)
        .join(Consignment.series)
        .all()
    )
    return [values[row.file_id] for row in rows]


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize("direction", ["asc", "desc"])
@pytest.mark.parametrize("scoped", [True, False])
@pytest.mark.parametrize("offset", [0, 5, 37, 100])
def test_pages_match_joined_query(records, field, direction, scoped, offset):
    accessible = ["permitted"] if scoped else None
    sort = {field: direction}
    reference = build_browse_records_base_query(accessible, sorting_orders=sort)
    count_query, page_query = build_browse_records_queries(
        accessible, sorting_orders=sort, offset=offset, limit=5
    )
    actual = page_query.all()
    expected = reference.offset(offset).limit(5).all()

    assert count_query.scalar() == reference.order_by(None).count()
    assert len(actual) == len(expected)
    assert len({row.file_id for row in actual}) == len(actual)
    assert sort_values(actual, field) == sort_values(expected, field)
    eligible_ids = {row.file_id for row in reference.all()}
    assert {row.file_id for row in actual} <= eligible_ids
    if scoped:
        assert all(row.transferring_body == "permitted" for row in actual)


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize("direction", ["asc", "desc"])
@pytest.mark.parametrize(
    "filters",
    [
        {"record_status": "open"},
        {"record_status": "closed"},
        {"date_from": "2020-01-05", "date_to": "2020-01-12"},
        {"date_filter_field": "opening_date", "date_from": "2020-01-20"},
        {"date_filter_field": "date_last_modified", "date_to": "2020-01-10"},
        {
            "date_filter_field": "transferred",
            "date_from": "2020-01-01",
            "date_to": "2020-01-28",
            "record_status": "closed",
        },
        {"record_status": "open", "date_from": "2099-01-01"},
    ],
)
def test_filters_apply_before_candidate_limits(
    records, field, direction, filters
):
    reference = build_browse_records_base_query(
        ["permitted"], filters, {field: direction}
    )
    count_query, page_query = build_browse_records_queries(
        ["permitted"], filters, {field: direction}, offset=3, limit=4
    )
    actual = page_query.all()
    expected = reference.offset(3).limit(4).all()

    assert count_query.scalar() == reference.order_by(None).count()
    assert len(actual) == len(expected)
    assert sort_values(actual, field) == sort_values(expected, field)
    assert {row.file_id for row in actual} <= {
        row.file_id for row in reference.all()
    }


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize(
    ("accessible", "filters"),
    [
        ([], {}),
        (["missing"], {}),
        (None, {"series": "missing"}),
        (None, {"transferring_body": "missing"}),
        (None, {"consignment_reference": "missing"}),
        (["permitted"], {"transferring_body": "denied"}),
    ],
)
def test_empty_scopes_never_become_unrestricted(
    records, field, accessible, filters
):
    count_query, page_query = build_browse_records_queries(
        accessible, filters, {field: "asc"}
    )

    assert count_query.scalar() == 0
    assert page_query.all() == []


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize(
    "scope", ["body", "series", "consignment", "permissions"]
)
def test_hierarchy_scope_and_bound_parameters(records, field, scope):
    consignment = records[0].consignment
    filters = {}
    accessible = None
    if scope == "body":
        filters["transferring_body"] = "  PERMITTED "
    elif scope == "series":
        filters["series"] = " ALPHA "
    elif scope == "consignment":
        filters["consignment_reference"] = (
            f" {consignment.ConsignmentReference.upper()} "
        )
    else:
        accessible = ["permitted"]
    count_query, page_query = build_browse_records_queries(
        accessible, filters, {field: "desc"}
    )
    reference = build_browse_records_base_query(accessible, filters)
    compiled = page_query.statement.compile(dialect=postgresql.dialect())

    assert str(consignment.ConsignmentId) not in str(compiled)
    assert "LATERAL" in str(compiled)
    assert "page_keys AS MATERIALIZED" in str(compiled)
    assert count_query.scalar() == reference.count()
    assert {row.file_id for row in page_query.all()} <= {
        row.file_id for row in reference.all()
    }
    count_sql = str(count_query.statement)
    assert "ORDER BY" not in count_sql
    assert "LIMIT" not in count_sql
    assert "to_char" not in count_sql
    assert '"Body"' not in count_sql


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize("scoped", [True, False])
def test_null_hierarchy_links_do_not_underfill_page_or_inflate_total(
    records, field, scoped
):
    # These nullable links are allowed by the metadata schema.
    orphan_series = SeriesFactory(body=None, Name="000")
    orphan_consignment = ConsignmentFactory(series=None)
    FileFactory(consignment=None, FileName="000")
    FileFactory(consignment=orphan_consignment, FileName="001")
    FileFactory(
        consignment=ConsignmentFactory(series=orphan_series), FileName="002"
    )
    accessible = ["permitted"] if scoped else None
    reference = build_browse_records_base_query(accessible)
    count_query, page_query = build_browse_records_queries(
        accessible, sorting_orders={field: "asc"}, limit=50
    )

    expected = {row.file_id for row in reference.all()}
    assert count_query.scalar() == len(expected)
    assert {row.file_id for row in page_query.all()} == expected


@pytest.mark.parametrize("field", SORT_FIELDS)
def test_date_ties_have_no_filename_or_id_ordering(records, field):
    _, query = build_browse_records_queries(
        ["permitted"], sorting_orders={field: "asc"}
    )
    sql = str(query.statement.compile(dialect=postgresql.dialect()))
    order_clauses = [
        clause.split("LIMIT")[0] for clause in sql.split("ORDER BY")[1:]
    ]
    assert order_clauses
    assert all('"FileId"' not in clause for clause in order_clauses)
    if field != "file_name":
        assert all('"FileName"' not in clause for clause in order_clauses)


@pytest.mark.parametrize("field", SORT_FIELDS)
def test_unrestricted_counts_preserve_hierarchy_joins(records, field):
    count_query, _ = build_browse_records_queries(sorting_orders={field: "asc"})
    sql = str(count_query.statement)
    assert all(
        f'"{table}"' in sql
        for table in ["File", "Consignment", "Series", "Body"]
    )


def test_other_shared_browse_sort_options_remain_accepted(records):
    count_query, page_query = build_browse_records_queries(
        ["permitted"], sorting_orders={"records_held": "desc"}
    )
    assert count_query.scalar() == 40
    assert len(page_query.all()) == 5


@pytest.mark.parametrize("field", SORT_FIELDS)
def test_multiple_permitted_bodies_share_the_same_scope(records, field):
    count_query, page_query = build_browse_records_queries(
        ["permitted", "denied"], sorting_orders={field: "desc"}, limit=50
    )
    rows = page_query.all()
    assert count_query.scalar() == 41
    assert len(rows) == 41
    assert {row.transferring_body for row in rows} == {"permitted", "denied"}


@pytest.mark.parametrize("field", SORT_FIELDS)
def test_candidates_use_offset_plus_limit_before_global_pagination(
    records, field
):
    _, page_query = build_browse_records_queries(
        ["permitted"], sorting_orders={field: "asc"}, offset=9, limit=7
    )
    compiled = page_query.statement.compile(dialect=postgresql.dialect())
    limits = {
        key: value
        for key, value in compiled.params.items()
        if key.startswith("param_")
    }
    assert list(limits.values()) == [16, 7, 9]
    if field != "series":
        assert "unnest(" in str(compiled)
        assert "consignment_ids" in compiled.params
        assert compiled.params["consignment_ids"]


@pytest.mark.parametrize("field", SORT_FIELDS)
@pytest.mark.parametrize("direction", ["asc", "desc"])
@pytest.mark.parametrize("scoped", [True, False])
def test_route_uses_paged_queries_for_every_sort(
    records,
    client,
    mock_standard_user,
    mock_all_access_user,
    field,
    direction,
    scoped,
):
    if scoped:
        mock_standard_user(client, "permitted")
    else:
        mock_all_access_user(client)

    response = client.get(
        "/browse/records",
        query_string={"sort": f"{field}-{direction}", "page": 2},
    )

    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    links = soup.select(
        "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
    )
    assert len(links) == 5
    assert len({link["href"] for link in links}) == 5
    expected_total = 40 if scoped else 41
    assert f"Showing 6\u201310 of {expected_total}" in soup.get_text(
        " ", strip=True
    )
    if scoped:
        permitted_links = {
            f"/record/{file.FileId}"
            for file in records
            if file.FileType.lower() == "file"
        }
        assert {link["href"] for link in links} <= permitted_links


@pytest.mark.parametrize(
    "field", [None, "date_last_modified", "opening_date", "transferred"]
)
@pytest.mark.parametrize(
    ("bounds", "expected_positions"),
    [
        ({"date_from": "2020-02-29"}, [1, 2, 3, 4]),
        ({"date_to": "2020-03-01"}, [0, 1, 2, 3]),
        (
            {"date_from": "2020-02-29", "date_to": "2020-03-01"},
            [1, 2, 3],
        ),
    ],
)
@pytest.mark.parametrize("scoped", [True, False])
def test_date_filters_use_inclusive_calendar_days(
    client, field, bounds, expected_positions, scoped
):
    consignment = ConsignmentFactory(
        series=SeriesFactory(body=BodyFactory(Name="permitted"))
    )
    dates = [
        datetime(2020, 2, 28, 23, 59, 59, 999999),
        datetime(2020, 2, 29),
        datetime(2020, 3, 1),
        datetime(2020, 3, 1, 23, 59, 59, 999999),
        datetime(2020, 3, 2),
        None,
    ]
    files = [
        FileFactory(
            consignment=consignment,
            EndDate=value if position % 2 else None,
            DateLastModified=value,
            OpeningDate=value,
        )
        for position, value in enumerate(dates)
    ]
    # The transferred filter uses EndDate alone, not its modification fallback.
    if field == "transferred":
        for file, value in zip(files, dates, strict=True):
            file.EndDate = value
    db.session.flush()

    count_query, page_query = build_browse_records_queries(
        ["permitted"] if scoped else None,
        {**bounds, "date_filter_field": field},
        {"file_name": "asc"},
        limit=10,
    )

    assert count_query.scalar() == len(expected_positions)
    assert {row.file_id for row in page_query.all()} == {
        files[position].FileId for position in expected_positions
    }
    count_sql = str(count_query.statement)
    assert "to_char" not in count_sql
    assert "CAST(" in count_sql


@pytest.mark.parametrize(
    "field", [None, "date_last_modified", "opening_date", "transferred"]
)
def test_upper_date_bound_handles_last_supported_calendar_day(client, field):
    file = FileFactory(
        EndDate=datetime.max,
        DateLastModified=datetime.max,
        OpeningDate=datetime.max,
    )
    db.session.flush()
    count_query, page_query = build_browse_records_queries(
        filters={
            "date_filter_field": field,
            "date_from": "9999-12-31",
            "date_to": "9999-12-31",
        }
    )

    assert count_query.scalar() == 1
    assert [row.file_id for row in page_query.all()] == [file.FileId]
