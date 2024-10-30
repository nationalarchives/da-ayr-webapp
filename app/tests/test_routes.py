import json
from io import BytesIO
from unittest.mock import patch

import boto3
import pytest
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient
from moto import mock_aws
from PIL import Image


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


def create_mock_s3_bucket_with_object(bucket_name, file):
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    file_object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )
    file_object.put(Body="record")
    return bucket


def create_mock_s3_bucket_with_imaage_object(bucket_name, file):
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
    image.save(image_file, format="PNG")
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

    @mock_aws
    @patch("app.main.util.render_utils.create_presigned_url")
    def test_route_generate_pdf_manifest(
        self,
        mock_create_presigned_url,
        app,
        client: FlaskClient,
        mock_all_access_user,
        record_files,
    ):
        mock_create_presigned_url.return_value = (
            "https://presigned-url.com/download.pdf"
        )

        mock_all_access_user(client)

        file = record_files[1]["file_object"]
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_object(bucket_name, file)

        response = client.get(f"{self.record_route_url}/{file.FileId}/manifest")
        assert response.status_code == 200

        expected_pdf_manifest = {
            "@context": ["http://iiif.io/api/presentation/3/context.json"],
            "behavior": ["individuals"],
            "description": "Manifest for open_file_once_closed.pdf",
            "id": f"http://localhost/record/{file.FileId}/manifest?render=True",
            "items": [
                {
                    "id": f"http://localhost/record/{file.FileId}/manifest?render=True",
                    "items": [
                        {
                            "id": "https://presigned-url.com/download.pdf",
                            "items": [
                                {
                                    "body": {
                                        "format": "application/pdf",
                                        "id": "https://presigned-url.com/download.pdf",
                                        "type": "Text",
                                    },
                                    "id": "https://presigned-url.com/download.pdf",
                                    "label": {"en": ["test"]},
                                    "motivation": "painting",
                                    "target": "https://presigned-url.com/download.pdf",
                                    "type": "Annotation",
                                }
                            ],
                            "label": {"en": ["test"]},
                            "type": "AnnotationPage",
                        }
                    ],
                    "label": {"en": ["test"]},
                    "type": "Canvas",
                }
            ],
            "label": {"none": ["open_file_once_closed.pdf"]},
            "requiredStatement": {
                "label": {"en": ["File name"]},
                "value": {"en": ["open_file_once_closed.pdf"]},
            },
            "type": "Manifest",
            "viewingDirection": "left-to-right",
        }

        actual_manifest = json.loads(response.text)

        assert response.status_code == 200
        assert actual_manifest == expected_pdf_manifest

    @mock_aws
    @patch("app.main.util.render_utils.create_presigned_url")
    def test_route_generate_image_manifest(
        self,
        mock_create_presigned_url,
        app,
        client: FlaskClient,
        mock_all_access_user,
        record_files,
    ):

        mock_all_access_user(client)

        file = record_files[5]["file_object"]
        bucket_name = "test_bucket"
        app.config["RECORD_BUCKET_NAME"] = bucket_name
        create_mock_s3_bucket_with_imaage_object(bucket_name, file)

        mock_create_presigned_url.return_value = (
            "https://presigned-url.com/download.png"
        )

        response = client.get(f"{self.record_route_url}/{file.FileId}/manifest")
        assert response.status_code == 200

        expected_image_manifest = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": f"http://localhost/record/{file.FileId}/manifest",
            "@type": "sc:Manifest",
            "description": f"Manifest for {file.FileName}",
            "label": file.FileName,
            "sequences": [
                {
                    "@id": "https://presigned-url.com/download.png",
                    "@type": "sc:Sequence",
                    "canvases": [
                        {
                            "@id": "https://presigned-url.com/download.png",
                            "@type": "sc:Canvas",
                            "height": 600,
                            "width": 800,
                            "images": [
                                {
                                    "@id": "https://presigned-url.com/download.png",
                                    "@type": "oa:Annotation",
                                    "motivation": "sc:painting",
                                    "on": "https://presigned-url.com/download.png",
                                    "resource": {
                                        "@id": "https://presigned-url.com/download.png",
                                        "format": "image/png",
                                        "height": 600,
                                        "type": "dctypes:Image",
                                        "width": 800,
                                    },
                                }
                            ],
                            "label": "Image 1",
                        }
                    ],
                }
            ],
        }

        actual_manifest = json.loads(response.text)

        assert response.status_code == 200
        assert actual_manifest == expected_image_manifest

    @pytest.mark.parametrize(
        "user_role, form_data, args_data, expected_redirect_route, expected_params",
        [
            # standard user with both form and args data, args has precedence for overlapping keys
            (
                "standard_user",
                {
                    "transferring_body_id": "form_value",
                    "other_param": "form_other_value",
                },
                {
                    "transferring_body_id": "args_value",
                    "another_param": "args_another_value",
                },
                "main.search_transferring_body",
                {
                    "_id": "args_value",
                    "other_param": "form_other_value",
                    "another_param": "args_another_value",
                },
            ),
            # standard user with only form data, no transferring_body_id in args
            (
                "standard_user",
                {"transferring_body_id": "form_value"},
                {},
                "main.search_transferring_body",
                {"_id": "form_value"},
            ),
            # standard user with only args data, transferring_body_id present
            (
                "standard_user",
                {},
                {"transferring_body_id": "args_value"},
                "main.search_transferring_body",
                {"_id": "args_value"},
            ),
            # all access user with args data (redirect to search_results_summary)
            (
                "all_access_user",
                {},
                {"some_param": "some_value"},
                "main.search_results_summary",
                {"some_param": "some_value"},
            ),
            # all access user with form data and args data (args takes precedence)
            (
                "all_access_user",
                {"some_param": "form_value"},
                {"some_param": "args_value"},
                "main.search_results_summary",
                {"some_param": "args_value"},
            ),
        ],
    )
    def test_search_route_with_various_cases(
        app,
        client: FlaskClient,
        user_role,
        form_data,
        args_data,
        expected_redirect_route,
        expected_params,
        mock_standard_user,
        mock_all_access_user,
    ):
        if user_role == "standard_user":
            mock_standard_user(client)
        else:
            mock_all_access_user(client)

        query_string = "&".join(
            [f"{key}={value}" for key, value in args_data.items()]
        )
        url = url_for("main.search") + "?" + query_string

        response = client.get(url, data=form_data)
        assert response.status_code == 302

        if expected_redirect_route == "main.search_transferring_body":
            redirected_url = url_for(
                expected_redirect_route, _id=expected_params["_id"]
            )
        else:
            redirected_url = url_for(expected_redirect_route, **expected_params)

        assert redirected_url in response.headers["Location"]

        for key, expected_value in expected_params.items():
            assert f"{key}={expected_value}" in response.headers["Location"]
