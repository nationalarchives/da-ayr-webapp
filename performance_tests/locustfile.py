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
    "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"""
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
                "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36""",
            }

            transferring_body_ids = [
                "<transferring_body_id>",
            ]

            series_ids = [
                "<series_id>",
            ]

            search_terms = ["test", "ab", "ld", "go", "tr"]

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
                f"/browse/transferring_body/{secrets.choice(transferring_body_ids)}",
                f"/browse/series/{secrets.choice(series_ids)}?sort={secrets.choice(series_sorts)}",
                f"""/browse?sort=transferring_body-asc&transferring_body_filter
                ={secrets.choice(transferring_body_filters)}&series_filter={secrets.choice(series_filters)}
                &date_from_day={date_from_day}&date_from_month={date_from_month}&date_from_year={date_from_year}
                &date_to_day={date_to_day}&date_to_month={date_to_month}&date_to_year={date_to_year}#browse-records""",
                f"""/browse?sort=series-asc&transferring_body_filter=&series_filter={secrets.choice(series_filters)}
                &date_from_year={date_from_year}&date_to_year={date_to_year}#browse-series""",
                f"/search_results_summary?query={secrets.choice(search_terms)}",
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
