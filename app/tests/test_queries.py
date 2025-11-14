import uuid
from datetime import datetime

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import (
    get_file_metadata,
)

per_page = 5
db_date_format = "%Y-%m-%d"
python_date_format = "%d/%m/%Y"


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
                        record_files[1]["closure_start_date"].Value,
                        db_date_format,
                    ).strftime(python_date_format)
                ),
                "closure_period": record_files[1]["closure_period"].Value,
                "opening_date": str(
                    datetime.strptime(
                        record_files[1]["opening_date"].Value, db_date_format
                    ).strftime(python_date_format)
                ),
                "end_date": str(
                    datetime.strptime(
                        record_files[1]["end_date"].Value,
                        db_date_format,
                    ).strftime(python_date_format)
                ),
                "date_of_record": str(
                    datetime.strptime(
                        record_files[1]["end_date"].Value
                        or record_files[1]["date_last_modified"].Value,
                        db_date_format,
                    ).strftime(python_date_format)
                ),
                "foi_exemption_code": record_files[1][
                    "foi_exemption_code"
                ].Value,
                "file_reference": file.FileReference,
                "former_reference": record_files[1]["former_reference"].Value,
                "translated_title": record_files[1]["translated_title"].Value,
                "related_material": record_files[1]["related_material"].Value,
                "restrictions_on_use": record_files[1][
                    "restrictions_on_use"
                ].Value,
                "note": record_files[1]["note"].Value,
                "held_by": record_files[1]["held_by"].Value,
                "legal_status": record_files[1]["legal_status"].Value,
                "rights_copyright": record_files[1]["rights_copyright"].Value,
                "language": record_files[1]["language"].Value,
                "transferring_body": file.consignment.series.body.Name,
                "series": file.consignment.series.Name,
                "consignment_reference": file.consignment.ConsignmentReference,
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
                "date_of_record": None,
                "foi_exemption_code": record_files[3][
                    "foi_exemption_code"
                ].Value,
                "file_reference": file.FileReference,
                "former_reference": record_files[3]["former_reference"].Value,
                "translated_title": record_files[3]["translated_title"].Value,
                "related_material": record_files[3]["related_material"].Value,
                "restrictions_on_use": record_files[3][
                    "restrictions_on_use"
                ].Value,
                "note": record_files[3]["note"].Value,
                "held_by": record_files[3]["held_by"].Value,
                "legal_status": record_files[3]["legal_status"].Value,
                "rights_copyright": record_files[3]["rights_copyright"].Value,
                "language": record_files[3]["language"].Value,
                "transferring_body": file.consignment.series.body.Name,
                "series": file.consignment.series.Name,
                "consignment_reference": file.consignment.ConsignmentReference,
                "end_date": None,
            }
        )

    def test_get_file_metadata_date_of_record_when_both_dates_are_none(
        self, client: FlaskClient, record_files
    ):
        """
        Given a file where both end_date and date_last_modified are None,
        When get_file_metadata is called,
        Then date_of_record should be None
        """
        from app.tests.factories import FileFactory, FileMetadataFactory

        # Create a file with both dates as None
        file = FileFactory(
            consignment=record_files[0]["file_object"].consignment,
            FileName="test_both_dates_none.txt",
            FileType="file",
        )
        FileMetadataFactory(file=file, PropertyName="end_date", Value=None)
        FileMetadataFactory(
            file=file, PropertyName="date_last_modified", Value=None
        )

        result = get_file_metadata(file_id=file.FileId)
        assert result["date_of_record"] is None

    def test_get_file_metadata_date_of_record_when_only_date_last_modified_exists(
        self, client: FlaskClient, record_files
    ):
        """
        Given a file where end_date is None but date_last_modified has a value,
        When get_file_metadata is called,
        Then date_of_record should use the date_last_modified value
        """
        from app.tests.factories import FileFactory, FileMetadataFactory

        # Create a file with only date_last_modified (end_date is None)
        file = FileFactory(
            consignment=record_files[0]["file_object"].consignment,
            FileName="test_only_date_last_modified.txt",
            FileType="file",
        )
        FileMetadataFactory(file=file, PropertyName="end_date", Value=None)
        FileMetadataFactory(
            file=file, PropertyName="date_last_modified", Value="2023-03-20"
        )

        result = get_file_metadata(file_id=file.FileId)
        assert result["date_of_record"] == "20/03/2023"

    def test_get_file_metadata_date_of_record_when_end_date_exists(
        self, client: FlaskClient, record_files
    ):
        """
        Given a file where both end_date and date_last_modified have values,
        When get_file_metadata is called,
        Then date_of_record should use end_date over date_last_modified
        """
        from app.tests.factories import FileFactory, FileMetadataFactory

        # Create a file with both dates (different values to test priority)
        file = FileFactory(
            consignment=record_files[0]["file_object"].consignment,
            FileName="test_end_date_priority.txt",
            FileType="file",
        )
        FileMetadataFactory(
            file=file, PropertyName="end_date", Value="2023-06-15"
        )
        FileMetadataFactory(
            file=file, PropertyName="date_last_modified", Value="2023-01-10"
        )

        result = get_file_metadata(file_id=file.FileId)
        # Should use end_date (15/06/2023) over date_last_modified (10/01/2023)
        assert result["date_of_record"] == "15/06/2023"
