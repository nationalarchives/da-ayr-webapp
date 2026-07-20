import json
from io import BytesIO
from unittest.mock import patch

import boto3
import pytest
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient
from moto import mock_aws
from PIL import Image

from app.tests.factories import FileFactory
from configs.base_config import UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS


def verify_cookies_header_row(data):
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Cookie name",
            "What it does/typical content",
            "Duration",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


def verify_cookies_data_rows(data, expected_rows):
    """
    this function check data rows for data table compared with expected rows
    :param data: response data
    :param expected_rows: expected rows to be compared
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    rows = table.find_all("td")

    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "

    assert [row_data] == expected_rows[0]


MINIMAL_VALID_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>\nendobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000116 00000 n \n"
    b"trailer\n<< /Root 1 0 R /Size 4 >>\nstartxref\n178\n%%EOF"
)


def create_mock_s3_bucket_with_object(bucket_name, file):
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    file_object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )
    # Use a minimal valid PDF if the extension is pdf
    if (
        getattr(file, "ffid_metadata", None)
        and getattr(file.ffid_metadata, "Extension", "").lower() == "pdf"
    ):
        file_object.put(Body=MINIMAL_VALID_PDF)
    else:
        file_object.put(Body="record")
    return bucket


def create_mock_s3_bucket_with_image_object(bucket_name, file):
    """
    Creates a dummy bucket and uploads an image file for tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    file_object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )

    image_file = BytesIO()
    image = Image.new("RGB", (800, 600), color=(73, 109, 137))
    puid = getattr(file.ffid_metadata, "PUID", None)
    format_map = {
        "fmt/3": "GIF",
        "fmt/4": "GIF",
        "fmt/43": "JPEG",
        "fmt/44": "JPEG",
        "x-fmt/391": "JPEG",
        "fmt/11": "PNG",
        "fmt/12": "PNG",
        "fmt/13": "PNG",
        "fmt/353": "TIFF",
        "fmt/567": "WEBP",
    }
    img_format = format_map.get(puid.lower(), "PNG") if puid else "PNG"
    print("IMG FORMAT:", img_format, "PUID:", puid)
    image.save(image_file, format=img_format)
    image_file.seek(0)

    file_object.put(Body=image_file.getvalue())
    return bucket


class TestRoutes:
    @property
    def record_route_url(self):
        return "/record"

    def test_route_accessibility(self, client: FlaskClient):
        response = client.get("/accessibility")
        assert response.status_code == 200

    def test_route_cookies(self, client: FlaskClient):
        response = client.get("/cookies")
        assert response.status_code == 200

    def test_route_privacy(self, client: FlaskClient):
        response = client.get("/privacy")
        assert response.status_code == 200

    def test_route_how_to_use(self, client: FlaskClient):
        response = client.get("/how-to-use-this-service")
        assert response.status_code == 200

    def test_route_terms_of_use(self, client: FlaskClient):
        response = client.get("/terms-of-use")
        assert response.status_code == 200

    def test_route_generate_pdf_manifest(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")

        response = client.get(f"{self.record_route_url}/{file.FileId}/manifest")
        assert response.status_code == 200

        manifest_url = f"http://localhost/record/{file.FileId}/manifest"
        canvas_id = f"{manifest_url}/canvas/1"
        pdf_url = f"http://localhost/record/{file.FileId}/pdf"

        expected_pdf_manifest = {
            "@context": "https://iiif.io/api/presentation/3/context.json",
            "id": manifest_url,
            "type": "Manifest",
            "label": {
                "en": [
                    "test.pdf",
                ],
            },
            "summary": {
                "en": [
                    "Manifest for test.pdf",
                ],
            },
            "service": [
                {
                    "@context": "http://iiif.io/api/search/1/context.json",
                    "@id": f"http://localhost/record/{file.FileId}/search",
                    "label": "Search within this record",
                    "profile": "http://iiif.io/api/search/1/search",
                }
            ],
            "rendering": [
                {
                    "id": pdf_url,
                    "type": "Text",
                    "label": {
                        "en": [
                            "test.pdf",
                        ],
                    },
                    "format": "application/pdf",
                }
            ],
            "items": [
                {
                    "id": canvas_id,
                    "type": "Canvas",
                    "label": {
                        "en": [
                            "test.pdf",
                        ],
                    },
                    "items": [
                        {
                            "id": f"{canvas_id}/annotationpage/1",
                            "type": "AnnotationPage",
                            "items": [
                                {
                                    "id": f"{canvas_id}/annotation/1",
                                    "type": "Annotation",
                                    "motivation": "painting",
                                    "body": {
                                        "id": pdf_url,
                                        "type": "Text",
                                        "format": "application/pdf",
                                    },
                                    "target": canvas_id,
                                }
                            ],
                        }
                    ],
                },
            ],
        }

        actual_manifest = json.loads(response.text)
        assert actual_manifest == expected_pdf_manifest

    @mock_aws
    @patch("app.main.routes.create_presigned_url")
    def test_route_generate_image_manifest(
        self,
        mock_create_presigned_url,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        puid_vs_ext = {
            "fmt/3": "gif",
            "fmt/4": "gif",
            "fmt/43": "jpeg",
            "fmt/44": "jpeg",
            "x-fmt/391": "jpeg",
            "fmt/11": "png",
            "fmt/12": "png",
            "fmt/13": "png",
            "fmt/353": "tiff",
            "fmt/567": "webp",
        }

        mock_all_access_user(client)
        for puid, ext in puid_vs_ext.items():
            file = FileFactory(ffid_metadata__PUID=puid, FileName=f"test.{ext}")
            bucket_name = "test-bucket"
            app.config["RECORD_BUCKET_NAME"] = bucket_name
            create_mock_s3_bucket_with_image_object(bucket_name, file)

            mock_create_presigned_url.return_value = (
                f"https://presigned-url.com/download.{ext}"
            )

            response = client.get(
                f"{self.record_route_url}/{file.FileId}/manifest"
            )
            assert response.status_code == 200

            expected_image_manifest = {
                "@context": "https://iiif.io/api/presentation/3/context.json",
                "@id": f"http://localhost/record/{file.FileId}/manifest",
                "@type": "sc:Manifest",
                "label": {"en": [file.FileName]},
                "description": f"Manifest for {file.FileName}",
                "sequences": [
                    {
                        "@id": f"https://presigned-url.com/download.{ext}",
                        "@type": "sc:Sequence",
                        "canvases": [
                            {
                                "@id": f"https://presigned-url.com/download.{ext}",
                                "@type": "sc:Canvas",
                                "label": "Image 1",
                                "width": 800,
                                "height": 600,
                                "images": [
                                    {
                                        "@id": f"https://presigned-url.com/download.{ext}",
                                        "@type": "oa:Annotation",
                                        "motivation": "sc:painting",
                                        "resource": {
                                            "@id": f"https://presigned-url.com/download.{ext}",
                                            "@type": "dctypes:Image",
                                            "format": f"image/{ext}",
                                            "width": 800,
                                            "height": 600,
                                        },
                                        "on": f"https://presigned-url.com/download.{ext}",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
            actual_manifest = json.loads(response.text)
            assert actual_manifest == expected_image_manifest

    @pytest.mark.parametrize(
        "form_data, args_data, expected_redirect_route, expected_params",
        [
            # all access user with args data (redirect to search_results_summary)
            (
                {},
                {"some_param": "some_value"},
                "main.search_results_summary",
                {},
            ),
            # all access user with form data and args data (args takes precedence)
            (
                {"some_param": "form_value"},
                {"some_param": "args_value"},
                "main.search_results_summary",
                {},
            ),
        ],
    )
    def test_search_route_with__tb_redirect_various_cases_all_access_user(
        app,
        client: FlaskClient,
        form_data,
        args_data,
        expected_redirect_route,
        expected_params,
        mock_all_access_user,
    ):
        mock_all_access_user(client)

        query_string = "&".join(
            [f"{key}={value}" for key, value in args_data.items()]
        )
        url = url_for("main.search") + "?" + query_string

        response = client.get(url, data=form_data)
        assert response.status_code == 302

        redirected_url = url_for(expected_redirect_route)

        assert redirected_url in response.headers["Location"]

        for key, expected_value in expected_params.items():
            assert f"{key}={expected_value}" in response.headers["Location"]

    @pytest.mark.parametrize(
        "form_data, args_data, expected_redirect_route, expected_params",
        [
            # standard user with both form and args data, args has precedence for overlapping keys
            # Note: only valid schema fields are passed through (unknown fields are filtered out)
            (
                {
                    "transferring_body_id": "form_value",
                    "query": "form_query_value",
                },
                {
                    "transferring_body_id": "args_value",
                    "search_area": "metadata",
                },
                "main.search_transferring_body",
                {
                    "_id": "args_value",
                    "search_area": "metadata",
                },
            ),
            # standard user with only form data, no transferring_body_id in args
            (
                {"transferring_body_id": "form_value"},
                {},
                "main.search_transferring_body",
                {"_id": "form_value"},
            ),
            # standard user with only args data, transferring_body_id present
            (
                {},
                {"transferring_body_id": "args_value"},
                "main.search_transferring_body",
                {"_id": "args_value"},
            ),
        ],
    )
    def test_search_route_with_various_cases_standard_user(
        app,
        client: FlaskClient,
        form_data,
        args_data,
        expected_redirect_route,
        expected_params,
        mock_standard_user,
    ):
        mock_standard_user(client)

        query_string = "&".join(
            [f"{key}={value}" for key, value in args_data.items()]
        )
        url = url_for("main.search") + "?" + query_string

        response = client.get(url, data=form_data)
        assert response.status_code == 302

        redirected_url = url_for(
            expected_redirect_route, _id=expected_params["_id"]
        )
        assert redirected_url in response.headers["Location"]

        for key, expected_value in expected_params.items():
            assert f"{key}={expected_value}" in response.headers["Location"]

    @mock_aws
    @patch("app.main.routes.boto3.client")
    @patch("app.main.routes.generate_pdf_manifest")
    def test_generate_manifest_pdf(
        self,
        mock_pdf,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Test that a PDF manifest is successfully generated.
        """
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276")
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(b"file content")}

        mock_pdf.return_value = ({"mock": "pdf_manifest"}, 200)
        response = client.get(f"/record/{file.FileId}/manifest")

        mock_pdf.assert_called_once()
        assert response.status_code == 200
        assert json.loads(response.text) == {"mock": "pdf_manifest"}

    @mock_aws
    @patch("app.main.routes.boto3.client")
    @patch("app.main.routes.generate_pdf_manifest")
    def test_generate_manifest_pdf_for_convertible_file_puids(
        self,
        mock_pdf,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Test that a PDF manifest is successfully generated
        When file_extension is in CONVERTIBLE_EXTENSIONS
        """
        mock_all_access_user(client)
        file = FileFactory(
            ffid_metadata__PUID="fmt/40", ffid_metadata__Extension="xls"
        )
        bucket_name = "test_bucket"
        app.config["ACCESS_COPY_BUCKET"] = bucket_name

        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(b"file content")}

        mock_pdf.return_value = ({"mock": "pdf_manifest"}, 200)
        response = client.get(f"/record/{file.FileId}/manifest")

        mock_pdf.assert_called_once()
        assert response.status_code == 200
        assert json.loads(response.text) == {"mock": "pdf_manifest"}

    @pytest.mark.parametrize(
        "image_format", UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS
    )
    @mock_aws
    @patch("app.main.routes.boto3.client")
    @patch("app.main.routes.generate_image_manifest")
    def test_generate_manifest_image(
        self,
        mock_image,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
        image_format,
    ):
        """
        Test that a image manifest is successfully generated.
        """
        mock_all_access_user(client)
        file = FileFactory(
            FileName=f"image.{image_format}",
            ffid_metadata__PUID=image_format,
        )
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(b"file content")}

        mock_image.return_value = ({"mock": "image_manifest"}, 200)
        response = client.get(f"/record/{file.FileId}/manifest")

        mock_image.assert_called_once()
        assert response.status_code == 200
        assert json.loads(response.text) == {"mock": "image_manifest"}

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_generate_manifest_unsupported(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
        caplog,
    ):
        """
        Test that an unsupported format will return a bad request and log the error
        """
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__Extension="xlsxx")
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(b"file content")}

        response = client.get(f"/record/{file.FileId}/manifest")
        assert response.status_code == 400
        assert "Failed to create manifest for file with ID" in caplog.text

    @mock_aws
    @patch("app.main.routes.create_presigned_url_for_access_copy")
    def test_record_route_with_convertible_file_failed_access_copy(
        self,
        mock_create_presigned_url,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(
            ffid_metadata__PUID="fmt/40", ffid_metadata__Extension="xls"
        )
        bucket_name = "test-bucket"
        app.config["ACCESS_COPY_BUCKET"] = bucket_name
        app.config["SUPPORTED_RENDER_PUIDS"] = {
            "fmt/3": "gif",
            "fmt/4": "gif",
            "fmt/43": "jpg",
            "fmt/44": "jpeg",
            "x-fmt/391": "jpg",
            "fmt/11": "png",
            "fmt/12": "png",
            "fmt/13": "png",
            "fmt/353": "tif",
            "fmt/567": "webp",
        }

        mock_create_presigned_url.side_effect = Exception(
            "failed to create access copy"
        )

        response = client.get(f"/record/{file.FileId}")

        assert response.status_code == 200
        assert b"Converted access copy not available." in response.data

    def test_method_not_allowed_returns_json(self, client: FlaskClient):
        """
        Test that a POST request to a GET-only route returns 405 JSON
        instead of crashing with 500 due to missing 405.html template
        """
        response = client.post("/")
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data["code"] == 405
        assert data["error"] == "Method Not Allowed"
        assert data["method"] == "POST"

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_search_within_record_no_query(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(MINIMAL_VALID_PDF)}

        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/search")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["@type"] == "sc:AnnotationList"
        assert body["resources"] == []
        assert body["hits"] == []
        assert body["within"]["total"] == 0

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_search_within_record_with_query(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        s3_mock = mock_boto_client.return_value
        s3_mock.get_object.return_value = {"Body": BytesIO(MINIMAL_VALID_PDF)}

        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/search?q=hello")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["@type"] == "sc:AnnotationList"
        assert "@context" in body
        assert "resources" in body
        assert "hits" in body

    def test_search_within_record_unsupported_puid(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        # fmt/999 is not in any supported PUID set
        file = FileFactory(
            ffid_metadata__PUID="fmt/999", FileName="test.unknown"
        )

        response = client.get(f"/record/{file.FileId}/search?q=hello")
        assert response.status_code == 400

    def test_search_within_record_file_not_found_returns_404(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        import uuid

        mock_all_access_user(client)
        response = client.get(f"/record/{uuid.uuid4()}/search?q=hello")
        assert response.status_code == 404

    @mock_aws
    @patch("app.main.routes.search_within_pdf")
    def test_search_within_record_convertible_puid_uses_access_copy_bucket(
        self,
        mock_search_within_pdf,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        from flask import jsonify

        mock_search_within_pdf.return_value = jsonify(
            {"@type": "sc:AnnotationList", "resources": [], "hits": []}
        )

        mock_all_access_user(client)
        file = FileFactory(
            ffid_metadata__PUID="fmt/40", ffid_metadata__Extension="xls"
        )
        access_bucket = "access-copy-bucket"
        app.config["ACCESS_COPY_BUCKET"] = access_bucket

        response = client.get(f"/record/{file.FileId}/search?q=hello")

        assert response.status_code == 200
        mock_search_within_pdf.assert_called_once()
        assert (
            mock_search_within_pdf.call_args.kwargs["bucket"] == access_bucket
        )

    @mock_aws
    def test_get_record_pdf_redirects_to_presigned_url(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        bucket_name = "test-bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"/record/{file.FileId}/pdf")

        assert response.status_code == 302
        location = response.headers["Location"]
        assert bucket_name in location
        assert (
            f"{file.consignment.ConsignmentReference}/{file.FileId}" in location
        )
        assert "response-content-type=application%2Fpdf" in location
        assert "response-content-disposition=inline" in location

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_get_record_pdf_file_not_in_db_returns_404(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        import uuid

        response = client.get(f"/record/{uuid.uuid4()}/pdf")
        assert response.status_code == 404

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_get_record_pdf_s3_not_found_returns_404(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        app.config["RECORD_BUCKET_NAME"] = "test-bucket"

        s3_mock = mock_boto_client.return_value
        s3_mock.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
        )

        response = client.get(f"/record/{file.FileId}/pdf")
        assert response.status_code == 404

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_get_record_pdf_s3_error_returns_500(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        app.config["RECORD_BUCKET_NAME"] = "test-bucket"

        s3_mock = mock_boto_client.return_value
        s3_mock.head_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Error"}},
            "HeadObject",
        )

        response = client.get(f"/record/{file.FileId}/pdf")
        assert response.status_code == 500

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_get_record_pdf_presigned_url_generation_failure_returns_500(
        self,
        mock_boto_client,
        app,
        client: FlaskClient,
        mock_all_access_user,
        caplog,
    ):
        mock_all_access_user(client)
        file = FileFactory(ffid_metadata__PUID="fmt/276", FileName="test.pdf")
        app.config["RECORD_BUCKET_NAME"] = "test-bucket"

        s3_mock = mock_boto_client.return_value
        s3_mock.generate_presigned_url.side_effect = Exception(
            "Error in presigned URL generation"
        )

        response = client.get(f"/record/{file.FileId}/pdf")

        assert response.status_code == 500
        assert "Failed to generate presigned URL" in caplog.text

    @mock_aws
    def test_get_record_pdf_convertible_puid_uses_access_copy_bucket(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
    ):
        mock_all_access_user(client)
        file = FileFactory(
            ffid_metadata__PUID="fmt/40", ffid_metadata__Extension="xls"
        )
        access_bucket = "access-copy-bucket"
        app.config["ACCESS_COPY_BUCKET"] = access_bucket
        create_mock_s3_bucket_with_object(access_bucket, file)

        response = client.get(f"/record/{file.FileId}/pdf")

        assert response.status_code == 302
        location = response.headers["Location"]
        assert access_bucket in location
        assert (
            f"{file.consignment.ConsignmentReference}/{file.FileId}" in location
        )
