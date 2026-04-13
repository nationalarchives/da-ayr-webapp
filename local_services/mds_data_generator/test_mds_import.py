"""
Integration test: runs mds_test_file_importer and asserts the expected records
exist in the database and OpenSearch.

Usage:
    python local_services/mds_data_generator/test_mds_import.py

"""

import os
import sys

from dotenv import load_dotenv
from mds_test_file_importer import (
    create_test_filepaths,
    index_in_opensearch,
    process_files,
)
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from app import create_app, db
from app.main.db.models import Consignment, FFIDMetadata, File, FileMetadata
from configs.env_config import EnvConfig

load_dotenv()

FILE_TYPE_COUNTS = {
    "csv": 1,
    "doc": 1,
    "docx": 1,
    "epub": 1,
    "jpg": 1,
    "odt": 1,
    "pdf": 1,
    "png": 1,
    "ppt": 1,
    "pptx": 1,
    "rtf": 1,
    "tif": 1,
    "txt": 1,
    "wk1": 1,
    "wk4": 1,
    "wp": 1,
    "xls": 1,
    "xlsx": 1,
    "xml": 1,
}

EXPECTED_METADATA_KEYS = {
    "source",
    "file_name",
    "file_type",
    "file_size",
    "rights_copyright",
    "legal_status",
    "held_by",
    "date_last_modified",
    "description",
    "closure_type",
    "title_closed",
    "description_closed",
    "language",
    "created_at",
    "last_transfer_date",
    "file_format",
    "file_extension",
    "closure_status",
    "closure_period",
    "foi_exemption_code",
    "foi_exemption_code_description",
    "title",
}


def get_opensearch_client():
    open_search_host_url = os.getenv("OPEN_SEARCH_HOST")
    aws_auth = AWS4Auth(
        os.getenv("AWS_ACCESS_KEY_ID"),
        os.getenv("AWS_SECRET_ACCESS_KEY"),
        os.getenv("AWS_REGION"),
        "es",
    )
    return OpenSearch(
        open_search_host_url,
        http_auth=aws_auth,
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )


def run():
    expected_file_count = sum(FILE_TYPE_COUNTS.values())

    # 1. Run the importer and capture the consignment reference
    print(f"Importing {FILE_TYPE_COUNTS} ...")
    file_paths = create_test_filepaths(FILE_TYPE_COUNTS)
    consignment_ref = process_files(file_paths)
    assert consignment_ref, "process_files() did not return a consignment_ref"
    print(f"Importer created consignment: {consignment_ref}")

    app = create_app(EnvConfig, True)
    with app.app_context():
        # 2. Find the consignment by its reference
        consignment = (
            db.session.query(Consignment)
            .filter_by(ConsignmentReference=consignment_ref)
            .first()
        )
        assert (
            consignment is not None
        ), f"Consignment '{consignment_ref}' not found in database"

        # 3. Assert correct number of File rows
        files = (
            db.session.query(File)
            .filter_by(ConsignmentId=consignment.ConsignmentId)
            .all()
        )
        assert (
            len(files) == expected_file_count
        ), f"Expected {expected_file_count} files, got {len(files)}"

        # 4. Assert each file has FFIDMetadata and all expected FileMetadata keys
        for f in files:
            ffid = (
                db.session.query(FFIDMetadata)
                .filter_by(FileId=f.FileId)
                .first()
            )
            assert ffid is not None, f"No FFIDMetadata for file {f.FileName}"
            assert (
                ffid.Extension in FILE_TYPE_COUNTS
            ), f"Unexpected extension '{ffid.Extension}' for file {f.FileName}"

            metadata_rows = (
                db.session.query(FileMetadata).filter_by(FileId=f.FileId).all()
            )
            actual_keys = {m.PropertyName for m in metadata_rows}
            missing_keys = EXPECTED_METADATA_KEYS - actual_keys
            assert (
                not missing_keys
            ), f"File {f.FileName} is missing metadata keys: {missing_keys}"

            print(f"  DB OK: {f.FileName} (ID: {f.FileId})")

        file_ids = [f.FileId for f in files]

    # 5. Index files in OpenSearch
    print("\nIndexing files in OpenSearch ...")
    index_in_opensearch(file_paths)

    # 6. Assert each file was indexed in OpenSearch
    print("Asserting OpenSearch documents ...")
    opensearch = get_opensearch_client()
    for file_id in file_ids:
        result = opensearch.get(index="documents", id=file_id)
        assert result[
            "found"
        ], f"File ID {file_id} not found in OpenSearch index"
        print(f"  OpenSearch OK: {file_id}")

    print("\nAll assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
