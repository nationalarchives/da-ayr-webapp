import uuid

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
    def test_build_fuzzy_search_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        query = build_fuzzy_search_query(query_string="fifth_file")
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
                browse_consignment_files[4].FileName,
                "Open",
                None,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_query_no_results(self, client: FlaskClient):
        """
        Given a filter value that does not match any field used for search terms
            in any file in the database
        When build_browse_all_query is called with it and is executed
        Then an empty list is returned
        """
        body = BodyFactory(Name="foo", Description="foo")
        series = SeriesFactory(Name="foo", Description="foo", body=body)
        consignment = ConsignmentFactory(
            ConsignmentReference="foo", series=series
        )
        FileFactory(FileType="file", FileName="foo", consignment=consignment)
        query = build_fuzzy_search_query(query_string="bar")
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
