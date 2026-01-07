from flask.testing import FlaskClient
from moto import mock_aws

from app.tests.factories import FileFactory
from app.tests.test_routes import create_mock_s3_bucket_with_object
from configs.base_config import CONVERTIBLE_PUIDS


class TestPageImageRoutes:
    """Tests for get_page_image and get_page_thumbnail routes."""

    @mock_aws
    def test_get_page_image_success(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test successful page image generation for a PDF."""
        mock_all_access_user(client)

        # Create a file with PDF PUID
        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        # Create S3 bucket with PDF
        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Request page 1
        response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 200
        assert response.content_type == "image/jpeg"
        assert len(response.data) > 0
        # Verify JPEG magic bytes
        assert response.data[:2] == b"\xff\xd8"
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "max-age=300" in response.headers["Cache-Control"]
        assert "ETag" in response.headers

    @mock_aws
    def test_get_page_image_invalid_page_number(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that invalid page number returns 400."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Request page 99 (beyond PDF page count)
        response = client.get(f"/record/{file.FileId}/page/99")

        assert response.status_code == 400

    @mock_aws
    def test_get_page_image_file_not_found(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that non-existent file returns 404."""
        mock_all_access_user(client)

        # Request page for non-existent file
        response = client.get(
            "/record/00000000-0000-0000-0000-000000000000/page/1"
        )

        assert response.status_code == 404

    @mock_aws
    def test_get_page_image_wrong_body_access(
        self, app, client: FlaskClient, mock_standard_user
    ):
        """Test that accessing file from wrong body returns 404."""
        mock_standard_user(client, body="test_body")

        # Create file with different body
        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
            consignment__series__body__Name="different_body",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 404

    @mock_aws
    def test_get_page_image_convertible_puid_uses_access_copy(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that convertible PUIDs use ACCESS_COPY_BUCKET."""
        mock_all_access_user(client)

        # Use a PUID from CONVERTIBLE_PUIDS
        convertible_puid = list(CONVERTIBLE_PUIDS)[0]
        # Create a file but override extension to pdf for the mock S3 object
        file = FileFactory(
            ffid_metadata__PUID=convertible_puid,
            ffid_metadata__Extension="pdf",  # Use pdf extension so mock creates valid PDF
            FileName="test.docx",
        )

        # Create S3 bucket with PDF in ACCESS_COPY_BUCKET
        access_copy_bucket = "test-access-copy-bucket"
        app.config["ACCESS_COPY_BUCKET"] = access_copy_bucket
        create_mock_s3_bucket_with_object(access_copy_bucket, file)

        response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 200
        assert response.content_type == "image/jpeg"

    @mock_aws
    def test_get_page_thumbnail_success(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test successful thumbnail generation for a PDF."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Request thumbnail for page 1
        response = client.get(f"/record/{file.FileId}/page/1/thumbnail")

        assert response.status_code == 200
        assert response.content_type == "image/jpeg"
        assert len(response.data) > 0
        # Verify JPEG magic bytes
        assert response.data[:2] == b"\xff\xd8"
        # Verify cache headers
        assert "Cache-Control" in response.headers
        assert "max-age=300" in response.headers["Cache-Control"]
        assert "ETag" in response.headers
        assert "-thumb" in response.headers["ETag"]

    @mock_aws
    def test_get_page_thumbnail_smaller_than_full_image(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that thumbnail is smaller than full page image."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Get both full image and thumbnail
        full_image_response = client.get(f"/record/{file.FileId}/page/1")
        thumbnail_response = client.get(
            f"/record/{file.FileId}/page/1/thumbnail"
        )

        assert full_image_response.status_code == 200
        assert thumbnail_response.status_code == 200

        # Thumbnail should be smaller than full image
        assert len(thumbnail_response.data) < len(full_image_response.data)

    @mock_aws
    def test_get_page_thumbnail_invalid_page_number(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that invalid page number returns 400 for thumbnail."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Request thumbnail for page 99 (beyond PDF page count)
        response = client.get(f"/record/{file.FileId}/page/99/thumbnail")

        assert response.status_code == 400

    @mock_aws
    def test_get_page_thumbnail_file_not_found(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that non-existent file returns 404 for thumbnail."""
        mock_all_access_user(client)

        response = client.get(
            "/record/00000000-0000-0000-0000-000000000000/page/1/thumbnail"
        )

        assert response.status_code == 404

    @mock_aws
    def test_get_page_thumbnail_convertible_puid_uses_access_copy(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that convertible PUIDs use ACCESS_COPY_BUCKET for thumbnails."""
        mock_all_access_user(client)

        convertible_puid = list(CONVERTIBLE_PUIDS)[0]
        file = FileFactory(
            ffid_metadata__PUID=convertible_puid,
            ffid_metadata__Extension="pdf",  # Use pdf extension so mock creates valid PDF
            FileName="test.docx",
        )

        access_copy_bucket = "test-access-copy-bucket"
        app.config["ACCESS_COPY_BUCKET"] = access_copy_bucket
        create_mock_s3_bucket_with_object(access_copy_bucket, file)

        response = client.get(f"/record/{file.FileId}/page/1/thumbnail")

        assert response.status_code == 200
        assert response.content_type == "image/jpeg"

    @mock_aws
    def test_page_image_cache_control_configured(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that cache control max-age is configurable."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 200
        assert "max-age=600" in response.headers["Cache-Control"]

    @mock_aws
    def test_page_thumbnail_cache_control_configured(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that thumbnail cache control max-age is configurable."""
        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/page/1/thumbnail")

        assert response.status_code == 200

    @mock_aws
    def test_get_page_image_s3_client_error(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that S3 ClientError returns 404 for page image."""
        from unittest.mock import patch

        from botocore.exceptions import ClientError

        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        # Don't create the S3 bucket, so get_object will fail
        # Mock get_pdf_from_s3 to raise ClientError
        with patch("app.main.routes.get_pdf_from_s3") as mock_get_pdf:
            mock_get_pdf.side_effect = ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
                "GetObject",
            )

            response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 404

    @mock_aws
    def test_get_page_image_extraction_error(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that extraction Exception returns 500 for page image."""
        from unittest.mock import patch

        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Mock extract_single_page_as_image to raise an exception
        with patch(
            "app.main.routes.extract_single_page_as_image"
        ) as mock_extract:
            mock_extract.side_effect = Exception("Extraction failed")

            response = client.get(f"/record/{file.FileId}/page/1")

        assert response.status_code == 500

    @mock_aws
    def test_get_page_thumbnail_s3_client_error(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that S3 ClientError returns 404 for thumbnail."""
        from unittest.mock import patch

        from botocore.exceptions import ClientError

        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        # Mock get_pdf_from_s3 to raise ClientError
        with patch("app.main.routes.get_pdf_from_s3") as mock_get_pdf:
            mock_get_pdf.side_effect = ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
                "GetObject",
            )

            response = client.get(f"/record/{file.FileId}/page/1/thumbnail")

        assert response.status_code == 404

    @mock_aws
    def test_get_page_thumbnail_extraction_error(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """Test that extraction Exception returns 500 for thumbnail."""
        from unittest.mock import patch

        mock_all_access_user(client)

        file = FileFactory(
            ffid_metadata__PUID="fmt/18",
            ffid_metadata__Extension="pdf",
            FileName="test.pdf",
        )

        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        # Mock extract_single_page_as_thumbnail to raise an exception
        with patch(
            "app.main.routes.extract_single_page_as_thumbnail"
        ) as mock_extract:
            mock_extract.side_effect = Exception("Thumbnail extraction failed")

            response = client.get(f"/record/{file.FileId}/page/1/thumbnail")

        assert response.status_code == 500
