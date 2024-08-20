import json
from io import BytesIO

import boto3
from bs4 import BeautifulSoup
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
    def test_route_generate_pdf_manifest(
        self,
        app,
        client: FlaskClient,
        mock_all_access_user,
        record_files,
    ):

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
                            "id": f"http://localhost/download/{file.FileId}?render=True",
                            "items": [
                                {
                                    "body": {
                                        "format": "application/pdf",
                                        "id": f"http://localhost/download/{file.FileId}",
                                        "type": "Text",
                                    },
                                    "id": f"http://localhost/download/{file.FileId}?render=True",
                                    "label": {"en": ["test"]},
                                    "motivation": "painting",
                                    "target": f"http://localhost/download/{file.FileId}?render=True",
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
    def test_route_generate_image_manifest(
        self,
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

        response = client.get(f"{self.record_route_url}/{file.FileId}/manifest")
        assert response.status_code == 200

        expected_image_manifest = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": f"http://localhost/download/{file.FileId}",
            "@type": "sc:Manifest",
            "description": f"Manifest for {file.FileName}",
            "label": file.FileName,
            "sequences": [
                {
                    "@id": f"http://localhost/download/{file.FileId}?render=True",
                    "@type": "sc:Sequence",
                    "canvases": [
                        {
                            "@id": f"http://localhost/download/{file.FileId}?render=True",
                            "@type": "sc:Canvas",
                            "height": 600,
                            "width": 800,
                            "images": [
                                {
                                    "@id": f"http://localhost/download/{file.FileId}?render=True",
                                    "@type": "oa:Annotation",
                                    "motivation": "sc:painting",
                                    "on": f"http://localhost/download/{file.FileId}?render=True",
                                    "resource": {
                                        "@id": f"http://localhost/download/{file.FileId}?render=True",
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
