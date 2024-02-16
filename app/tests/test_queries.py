import uuid
from datetime import datetime

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import build_fuzzy_search_query, get_file_metadata
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)

per_page = 5


class TestFuzzySearch:
    @pytest.mark.parametrize(
        "file_metadata_property",
        [
            "Value",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_file_metadata_properties(
        self, client: FlaskClient, file_metadata_property
    ):
        """
        Given a query string that matches one of the parametrized file_metadata_property
            on a FileMetadata object in the database
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file is returned
        """
        file_metadata_property_map = {file_metadata_property: "foo"}
        file = FileFactory(FileType="file")
        FileMetadataFactory(file=file, **file_metadata_property_map)
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "file_property",
        [
            "FileName",
            "FileReference",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_file_properties(
        self, client: FlaskClient, file_property
    ):
        """
        Given a query string that matches one of the parametrized file_property
            on a File object in the database
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file is returned
        """
        file_property_map = {file_property: "foo"}
        file = FileFactory(FileType="file", **file_property_map)
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "consignment_property",
        [
            "ConsignmentReference",
            "ConsignmentType",
            "ContactName",
            "ContactEmail",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_consignment_properties(
        self, client: FlaskClient, consignment_property
    ):
        """
        Given a query string that matches one of the parametrized consignment_property
            on a Consignment object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Consignment is returned
        """
        consignment_property_map = {consignment_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(**consignment_property_map),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "consignment_date_property",
        [
            "TransferStartDatetime",
            "TransferCompleteDatetime",
            "ExportDatetime",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_consignment_date_properties(
        self, client: FlaskClient, consignment_date_property
    ):
        """
        Given a query string that matches one of the parametrized consignment_date_property
            on a Consignment object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Consignment is returned
        """
        consignment_date_property_map = {
            consignment_date_property: datetime(2022, 2, 18)
        }
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(**consignment_date_property_map),
        )
        query_string = "18/02/2022"
        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "body_property",
        [
            "Name",
            "Description",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_body_properties(
        self, client: FlaskClient, body_property
    ):
        """
        Given a query string that matches one of the parametrized body_property
            on a Body object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Body is returned
        """
        body_property_map = {body_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(
                series=SeriesFactory(body=BodyFactory(**body_property_map))
            ),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "series_property",
        [
            "Name",
            "Description",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_series_properties(
        self, client: FlaskClient, series_property
    ):
        """
        Given a query string that matches one of the parametrized series_property
            on a Series object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Body is returned
        """
        series_property_map = {series_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(
                series=SeriesFactory(**series_property_map)
            ),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    def test_build_fuzzy_search_query_no_results(self, client: FlaskClient):
        """
        Given a query string that does not match any field in any file object
            in the database
        When fuzzy_search is called with it and is executed
        Then an empty list is returned
        """
        FileFactory(FileName="foo", FileType="file")
        query_string = "bar"
        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == []


class TestGetFileMetadata:
    def test_invalid_uuid_raises_not_found_error(self, client: FlaskClient):
        """
        Given a UUID not corresponding to the id of a file in the database
        When get_file_metadata is called with it
        Then werkzeug.exceptions.NotFound is raised
        """
        non_existent_file_id = uuid.uuid4()
        with pytest.raises(werkzeug.exceptions.NotFound):
            get_file_metadata(non_existent_file_id)

    def test_valid_uuid_returns_metadata(self, client: FlaskClient):
        """
        Given a file with associated metadata,
        When get_file_metadata is called with its UUID,
        Then a tuple of specific metadata for the file is returned
        """
        file = FileFactory(
            FileName="test_file.txt",
            FilePath="data/content/test_file.txt",
            FileType="file",
        )

        metadata = {
            "date_last_modified": "2023-02-25T10:12:47",
            "closure_type": "Closed",
            "description": "Test description",
            "held_by": "Test holder",
            "legal_status": "Test legal status",
            "rights_copyright": "Test copyright",
            "language": "English",
        }

        [
            FileMetadataFactory(
                file=file,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in metadata.items()
        ]

        assert get_file_metadata(file_id=file.FileId) == {
            "file_id": file.FileId,
            "file_name": "test_file.txt",
            "file_path": "data/content/test_file.txt",
            "status": "Closed",
            "description": "Test description",
            "date_last_modified": "2023-02-25T10:12:47",
            "held_by": "Test holder",
            "legal_status": "Test legal status",
            "rights_copyright": "Test copyright",
            "language": "English",
            "consignment": file.consignment.ConsignmentReference,
            "consignment_id": file.ConsignmentId,
            "transferring_body": file.consignment.series.body.Name,
            "transferring_body_id": file.consignment.series.body.BodyId,
            "series": file.consignment.series.Name,
            "series_id": file.consignment.series.SeriesId,
        }

    def test_valid_uuid_returns_none_for_any_metadata(
        self, client: FlaskClient
    ):
        """
        Given a file with no associatedf file metadata,
        When get_file_metadata is called with its UUID,
        Then a dict of metadata for the file is returned
            and all the file metadata fields are None
        """
        file = FileFactory(
            FileName="test_file.txt",
            FilePath="data/content/test_file.txt",
            FileType="file",
        )

        assert get_file_metadata(file_id=file.FileId) == {
            "file_id": file.FileId,
            "file_name": "test_file.txt",
            "file_path": "data/content/test_file.txt",
            "status": None,
            "description": None,
            "date_last_modified": None,
            "held_by": None,
            "legal_status": None,
            "rights_copyright": None,
            "language": None,
            "consignment": file.consignment.ConsignmentReference,
            "consignment_id": file.ConsignmentId,
            "transferring_body": file.consignment.series.body.Name,
            "transferring_body_id": file.consignment.series.body.BodyId,
            "series": file.consignment.series.Name,
            "series_id": file.consignment.series.SeriesId,
        }
