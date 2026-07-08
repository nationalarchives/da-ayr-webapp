import os
from time import perf_counter

import pytest
from flask.testing import FlaskClient

from app.main.db.queries import build_flattened_browse_records_query
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)


class TestFlattenedBrowseRecordsQuery:
    def test_returns_flattened_records_for_accessible_bodies(
        self, client: FlaskClient
    ):
        first_body = BodyFactory(Name="first_body")
        second_body = BodyFactory(Name="second_body")

        first_series = SeriesFactory(Name="series_a", body=first_body)
        second_series = SeriesFactory(Name="series_b", body=second_body)

        first_consignment = ConsignmentFactory(
            series=first_series,
            ConsignmentReference="C-0001",
        )
        second_consignment = ConsignmentFactory(
            series=second_series,
            ConsignmentReference="C-0002",
        )

        first_file = FileFactory(
            consignment=first_consignment,
            FileType="file",
            FileName="first-file.doc",
        )
        second_file = FileFactory(
            consignment=second_consignment,
            FileType="file",
            FileName="second-file.doc",
        )

        FileMetadataFactory(
            file=first_file,
            PropertyName="date_last_modified",
            Value="2024-01-10",
        )
        FileMetadataFactory(
            file=first_file,
            PropertyName="closure_type",
            Value="Open",
        )

        FileMetadataFactory(
            file=second_file,
            PropertyName="date_last_modified",
            Value="2024-01-15",
        )
        FileMetadataFactory(
            file=second_file,
            PropertyName="closure_type",
            Value="Closed",
        )

        query = build_flattened_browse_records_query(
            accessible_transferring_body_names=["first_body"]
        )

        results = query.all()

        assert len(results) == 1
        assert results[0].transferring_body == "first_body"
        assert results[0].consignment_reference == "C-0001"
        assert results[0].file_name == "first-file.doc"
        assert results[0].closure_type == "Open"

    def test_returns_no_rows_for_empty_access_list(self, client: FlaskClient):
        body = BodyFactory(Name="first_body")
        series = SeriesFactory(Name="series_a", body=body)
        consignment = ConsignmentFactory(
            series=series,
            ConsignmentReference="C-0001",
        )
        file = FileFactory(
            consignment=consignment,
            FileType="file",
            FileName="first-file.doc",
        )
        FileMetadataFactory(
            file=file,
            PropertyName="date_last_modified",
            Value="2024-01-10",
        )

        results = build_flattened_browse_records_query(
            accessible_transferring_body_names=[]
        ).all()

        assert results == []


@pytest.mark.skipif(
    os.getenv("AYR_RUN_PERFORMANCE_VALIDATION") != "1",
    reason="Set AYR_RUN_PERFORMANCE_VALIDATION=1 to run performance validation",
)
def test_flattened_query_performance_validation(client: FlaskClient):
    body = BodyFactory(Name="perf_body")
    series = SeriesFactory(Name="perf_series", body=body)

    record_count = int(os.getenv("AYR_PERF_RECORD_COUNT", "2000"))
    threshold_seconds = float(os.getenv("AYR_PERF_THRESHOLD_SECONDS", "1.5"))

    for i in range(record_count):
        consignment = ConsignmentFactory(
            series=series,
            ConsignmentReference=f"PERF-{i:05d}",
        )
        file = FileFactory(
            consignment=consignment,
            FileType="file",
            FileName=f"perf-file-{i:05d}.txt",
        )
        FileMetadataFactory(
            file=file,
            PropertyName="date_last_modified",
            Value="2024-01-10",
        )
        FileMetadataFactory(
            file=file,
            PropertyName="closure_type",
            Value="Open" if i % 2 == 0 else "Closed",
        )

    start_time = perf_counter()
    results = build_flattened_browse_records_query(
        accessible_transferring_body_names=["perf_body"]
    ).limit(10).all()
    elapsed = perf_counter() - start_time

    assert len(results) == 10
    assert elapsed <= threshold_seconds
