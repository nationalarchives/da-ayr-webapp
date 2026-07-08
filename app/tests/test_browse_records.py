from flask.testing import FlaskClient

from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)


class TestBrowseRecords:
    @property
    def route_url(self):
        return "/browse/records"

    def _create_record(self, body_name: str, consignment_reference: str):
        body = BodyFactory(Name=body_name)
        series = SeriesFactory(Name=f"series-{body_name}", body=body)
        consignment = ConsignmentFactory(
            series=series,
            ConsignmentReference=consignment_reference,
        )
        file = FileFactory(
            consignment=consignment,
            FileType="file",
            FileName=f"file-{consignment_reference}.txt",
        )
        FileMetadataFactory(
            file=file,
            PropertyName="date_last_modified",
            Value="2024-01-10",
        )
        FileMetadataFactory(
            file=file,
            PropertyName="closure_type",
            Value="Open",
        )
        return file

    def test_all_access_user_can_fetch_flattened_records(
        self, client: FlaskClient, mock_all_access_user
    ):
        mock_all_access_user(client)
        self._create_record("first_body", "C-0001")
        self._create_record("second_body", "C-0002")

        response = client.get(self.route_url)

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["per_page"] == 10
        assert payload["total_records"] == 2
        assert len(payload["results"]) == 2

    def test_standard_user_only_gets_accessible_body_records(
        self, client: FlaskClient, mock_standard_user
    ):
        self._create_record("first_body", "C-0001")
        self._create_record("second_body", "C-0002")
        mock_standard_user(client, "first_body")

        response = client.get(self.route_url)

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["total_records"] == 1
        assert payload["results"][0]["transferring_body"] == "first_body"

    def test_per_page_is_fixed_even_when_query_param_is_provided(
        self, client: FlaskClient, mock_all_access_user
    ):
        mock_all_access_user(client)
        for i in range(12):
            self._create_record("first_body", f"C-{i:04d}")

        response = client.get(f"{self.route_url}?page=1&per_page=100")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["per_page"] == 10
        assert len(payload["results"]) == 10

    def test_invalid_page_redirects_to_first_page(
        self, client: FlaskClient, mock_all_access_user
    ):
        mock_all_access_user(client)
        self._create_record("first_body", "C-0001")

        response = client.get(f"{self.route_url}?page=999")

        assert response.status_code == 302
        assert "/browse/records?page=1" in response.headers["Location"]
