import uuid
from datetime import datetime

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import (
    build_fuzzy_search_summary_query,
    build_fuzzy_search_transferring_body_query,
    get_file_metadata,
)
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)

per_page = 5


class TestFuzzySearchTransferringBody:
    def test_build_fuzzy_search_transferring_body_query_with_single_term_search_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_fuzzy_search_transferring_body_query is called
        with single search term and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        query = build_fuzzy_search_transferring_body_query(
            query_string="fifth_file", transferring_body_id=transferring_body_id
        )
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.body.Description,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.series.Description,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
                browse_consignment_files[4].FileId,
                browse_consignment_files[4].FileName,
                "Open",
                None,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_transferring_body_query_with_multiple_terms_search_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_fuzzy_search_transferring_body_query is called
        with multiple search terms and is executed
        Then matching list results rows is returned based on the search within the search
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        query = build_fuzzy_search_transferring_body_query(
            query_string="fi, xls", transferring_body_id=transferring_body_id
        )
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.body.Description,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.series.Description,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
                browse_consignment_files[3].FileId,
                browse_consignment_files[3].FileName,
                "Closed",
                "12/04/2023",
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_transferring_body_query_no_results(
        self, client: FlaskClient
    ):
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
        transferring_body_id = body.BodyId
        query = build_fuzzy_search_transferring_body_query(
            query_string="bar", transferring_body_id=transferring_body_id
        )
        results = query.all()
        assert results == []

    def test_build_fuzzy_search_summary_query_with_single_term_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match multiple in the database
        When build_fuzzy_search_summary_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        query = build_fuzzy_search_summary_query(query_string="fi")
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                5,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_summary_query_with_multiple_terms_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match multiple in the database
        When build_fuzzy_search_summary_query is called
        with multiple search terms and is executed
        Then matching list results rows is returned based on the search within the search
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        query = build_fuzzy_search_summary_query(query_string="fi, file")
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                5,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_summary_query_no_results(
        self, client: FlaskClient
    ):
        """
        Given a filter value that does not match transferring body in the database
        When build_fuzzy_search_summary_query is called with it and is executed
        Then an empty list is returned
        """
        query = build_fuzzy_search_summary_query(query_string="junk")
        results = query.all()
        assert results == []


class TestGetFileMetadata:
    def test_get_file_metadata_return_no_results(self, client: FlaskClient):
        """
        Given a UUID not corresponding to the id of a file in the database
        When get_file_metadata is called with it
        Then werkzeug.exceptions.NotFound is raised
        """
        non_existent_file_id = uuid.uuid4()
        with pytest.raises(werkzeug.exceptions.NotFound):
            get_file_metadata(non_existent_file_id)

    def test_get_file_metadata_return_results(
        self, client: FlaskClient, record_files
    ):
        """
        Given a file with associated metadata,
        When get_file_metadata is called with its UUID,
        Then a tuple of specific metadata for the file is returned
        """
        file = record_files[1]["file_object"]

        assert get_file_metadata(file_id=file.FileId) == (
            {
                "file_id": file.FileId,
                "file_name": file.FileName,
                "file_path": file.FilePath,
                "citeable_reference": file.CiteableReference,
                "alternative_title": record_files[1]["alternative_title"].Value,
                "description": record_files[1]["description"].Value,
                "alternative_description": record_files[1][
                    "alternative_description"
                ].Value,
                "closure_type": record_files[1]["closure_type"].Value,
                "closure_start_date": str(
                    datetime.strptime(
                        record_files[1]["closure_start_date"].Value, "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                ),
                "closure_period": record_files[1]["closure_period"].Value,
                "opening_date": str(
                    datetime.strptime(
                        record_files[1]["opening_date"].Value, "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                ),
                "date_last_modified": str(
                    datetime.strptime(
                        record_files[1]["date_last_modified"].Value, "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                ),
                "foi_exemption_code": record_files[1][
                    "foi_exemption_code"
                ].Value,
                "transferring_body_id": file.consignment.series.body.BodyId,
                "transferring_body": file.consignment.series.body.Name,
                "series_id": file.consignment.series.SeriesId,
                "series": file.consignment.series.Name,
                "consignment_id": file.ConsignmentId,
                "consignment_reference": file.consignment.ConsignmentReference,
                "file_reference": file.FileReference,
                "former_reference": record_files[1]["former_reference"].Value,
                "translated_title": record_files[1]["translated_title"].Value,
                "held_by": record_files[1]["held_by"].Value,
                "legal_status": record_files[1]["legal_status"].Value,
                "rights_copyright": record_files[1]["rights_copyright"].Value,
                "language": record_files[1]["language"].Value,
            }
        )

    def test_get_file_metadata_return_results_with_no_metadata(
        self, client: FlaskClient, record_files
    ):
        """
        Given a file with no associated file metadata,
        When get_file_metadata is called with its UUID,
        Then a dict of metadata for the file is returned
            and all the file metadata fields are None
        """
        file = record_files[3]["file_object"]

        assert get_file_metadata(file_id=file.FileId) == (
            {
                "file_id": file.FileId,
                "file_name": file.FileName,
                "file_path": file.FilePath,
                "citeable_reference": file.CiteableReference,
                "alternative_title": record_files[3]["alternative_title"].Value,
                "description": record_files[3]["description"].Value,
                "alternative_description": record_files[3][
                    "alternative_description"
                ].Value,
                "closure_type": record_files[3]["closure_type"].Value,
                "closure_start_date": record_files[3][
                    "closure_start_date"
                ].Value,
                "closure_period": record_files[3]["closure_period"].Value,
                "opening_date": record_files[3]["opening_date"].Value,
                "date_last_modified": record_files[3][
                    "date_last_modified"
                ].Value,
                "foi_exemption_code": record_files[3][
                    "foi_exemption_code"
                ].Value,
                "transferring_body_id": file.consignment.series.body.BodyId,
                "transferring_body": file.consignment.series.body.Name,
                "series_id": file.consignment.series.SeriesId,
                "series": file.consignment.series.Name,
                "consignment_id": file.ConsignmentId,
                "consignment_reference": file.consignment.ConsignmentReference,
                "file_reference": file.FileReference,
                "former_reference": record_files[3]["former_reference"].Value,
                "translated_title": record_files[3]["translated_title"].Value,
                "held_by": record_files[3]["held_by"].Value,
                "legal_status": record_files[3]["legal_status"].Value,
                "rights_copyright": record_files[3]["rights_copyright"].Value,
                "language": record_files[3]["language"].Value,
            }
        )
