import os
import secrets

from locust import HttpUser, between, task

CERT_PATH = False
AYR_AAU_USER_USERNAME = os.getenv("AYR_AAU_USER_USERNAME")
AYR_AAU_USER_PASSWORD = os.getenv("AYR_AAU_USER_PASSWORD")
KEYCLOAK_AUTH_URL = os.getenv("KEYCLOAK_AUTH_URL")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

headers_string = {
    "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"""  # noqa: E501
}


class User(HttpUser):
    # Set the wait time between task executions (e.g., between 1 and 5 seconds)
    wait_time = between(1, 5)

    # Define tasks
    @task
    def index(self):
        headers = headers_string

        with self.client.get(
            "/", headers=headers, catch_response=True, verify=False
        ) as response:
            if response.status_code == 200:
                response.success()
                print(response.text)
                print("Page loaded successfully")
            else:
                response.failure(f"Failed to load page: {response.status_code}")
                print(response.text)

    @task
    def accessibility(self):
        headers = headers_string
        self.client.get("/accessibility", headers=headers, verify=CERT_PATH)

    @task
    def terms_of_use(self):
        headers = headers_string
        self.client.get("/terms-of-use", headers=headers, verify=CERT_PATH)

    @task
    def how_to_use(self):
        headers = headers_string
        self.client.get(
            "/how-to-use-this-service", headers=headers, verify=CERT_PATH
        )

    @task
    def privacy(self):
        headers = headers_string
        self.client.get("/privacy", headers=headers, verify=CERT_PATH)

    @task
    def cookies(self):
        headers = headers_string
        self.client.get("/cookies", headers=headers, verify=CERT_PATH)

    @task
    def signed_out(self):
        headers = headers_string
        self.client.get("/signed-out", headers=headers, verify=CERT_PATH)


class KeycloakUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.token, self.refresh_token = self.authenticate()

    def authenticate(self):
        token_url = KEYCLOAK_AUTH_URL
        client_id = KEYCLOAK_CLIENT_ID
        client_secret = KEYCLOAK_CLIENT_SECRET
        username = AYR_AAU_USER_USERNAME
        password = AYR_AAU_USER_PASSWORD

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "grant_type": "password",
        }

        response = self.client.post(token_url, data=payload)

        if response.status_code == 200:
            json_response = response.json()
            access_token = json_response["access_token"]
            refresh_token = json_response["refresh_token"]
            return access_token, refresh_token
        else:
            print(
                f"Failed to authenticate: {response.status_code}, {response.text}"
            )
            return None

    @task
    def browse_pages(self):
        if self.token:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36""",  # noqa: E501
            }

            transferring_body_ids = [
                "4654e9f9-335b-4ab1-acd8-edff54f908d4",
                "8ccc8cd1-c0ee-431d-afad-70cf404ba337",
                "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50",
                "935839c0-c070-4d61-924f-f16ee8d8a160",
            ]

            series_ids = [
                "93ed0101-2318-45ab-8730-c681958ded7e",
                "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
                "1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7",
                "7f0a484e-2bbb-493b-90bd-7e6832345b1d",
            ]

            consignment_ids = [
                "2fd4e03e-5913-4c04-b4f2-5a823fafd430",
                "016031db-1398-4fe4-b743-630aa82ea32a",
                "d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f",
                "7c665764-2103-45f9-800b-f36893dd4436",
            ]

            record_ids = [
                "123e4567-e89b-12d3-a456-426614174000",
                "100251bb-5b93-48a9-953f-ad5bd9abfbdc",
                "99340295-cfb4-4cd1-8739-c1077093a947",
                "6a25d42c-14bb-4a62-b929-fa524fe90a9f",
            ]

            search_terms = ["test", "ab", "ld", "go", "tr"]
            search_areas = ["everywhere", "metadata", "record"]

            transferring_body_filters = [
                "a",
                "b",
            ]
            series_filters = ["ab", "y", "b", "l"]

            series_sorts = [
                "consignment_reference-desc",
                "consignment_reference-asc",
                "last_record_transferred-asc",
                "last_record_transferred-desc",
                "records_held-asc",
                "records_held-desc",
            ]

            date_from_year = secrets.randbelow(31) + 1990
            date_to_year = secrets.randbelow(4) + date_from_year
            date_from_month = secrets.randbelow(12) + 1
            date_to_month = secrets.randbelow(12) + 1
            date_from_day = secrets.randbelow(28) + 1
            date_to_day = secrets.randbelow(28) + 1

            urls = [
                "/browse",
                f"/browse/transferring_body/{secrets.choice(transferring_body_ids)}",
                f"/browse/series/{secrets.choice(series_ids)}?sort={secrets.choice(series_sorts)}",
                f"/browse/consignment/{secrets.choice(consignment_ids)}",
                f"/browse/consignment/{secrets.choice(consignment_ids)}?series_filter=AYR+1&date_from_day=01&date_from_month=01&date_from_year=2020&date_to_day=01&date_to_month=01&date_to_year=2026&page=1&per_page=10",  # noqa: E501
                f"/browse?sort=transferring_body-asc&transferring_body_filter={secrets.choice(transferring_body_filters)}&series_filter={secrets.choice(series_filters)}&date_from_day={date_from_day}&date_from_month={date_from_month}&date_from_year={date_from_year}&date_to_day={date_to_day}&date_to_month={date_to_month}&date_to_year={date_to_year}#browse-records",  # noqa: E501
                f"/browse?sort=series-asc&transferring_body_filter=&series_filter={secrets.choice(series_filters)}&date_from_year={date_from_year}&date_to_year={date_to_year}#browse-series",  # noqa: E501
                "/browse?transferring_body_filter=&series_filter=MOCK1+123&date_from_day=01&date_from_month=01&date_from_year=2020&date_to_day=01&date_to_month=01&date_to_year=2026#browse-records",  # noqa: E501
                "/search?query=test&search_area=everywhere&search_filter=test",
                "/search?query=ab&search_area=record&search_filter=go",
                "/search?query=ld&search_area=metadata&search_filter=tr",
                f"/search_results_summary?query={secrets.choice(search_terms)}",
                "/search_results_summary?query=test&search_area=everywhere&open_all=true&page=1&per_page=10",  # noqa: E501
                "/search_results_summary?query=ab&search_area=record&search_filter=test&sort=file_name&page=1&per_page=10",  # noqa: E501
                "/search_results_summary?query=go&search_area=metadata&open_all=open_all&sort=file_name&page=1&per_page=10",  # noqa: E501
                f"/search/transferring_body/{secrets.choice(transferring_body_ids)}?query={secrets.choice(search_terms)}&sort=file_name&search_area={secrets.choice(search_areas)}",  # noqa: E501
                "/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test",  # noqa: E501
                "/search/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50?query=test&sort=file_name&search_area=record",  # noqa: E501
                f"/record/{secrets.choice(record_ids)}",
                f"/record/{secrets.choice(record_ids)}#record-view",
            ]

            url = secrets.choice(urls)

            with self.client.get(
                url, headers=headers, catch_response=True, verify=False
            ) as response:
                if response.status_code == 200:
                    response.success()
                    print(f"Page {url} loaded successfully")
                else:
                    response.failure(
                        f"Failed to load page {url}: {response.status_code}"
                    )
                    print(response.text)
