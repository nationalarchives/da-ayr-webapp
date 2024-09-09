import secrets
import os

from locust import HttpUser, between, task

CERT_PATH = False
AYR_AAU_USER_USERNAME = os.getenv("AYR_AAU_USER_USERNAME")
AYR_AAU_USER_PASSWORD = os.getenv("AYR_AAU_USER_PASSWORD")
KEYCLOAK_AUTH_URL = os.getenv("KEYCLOAK_AUTH_URL")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")


class User(HttpUser):
    # Set the wait time between task executions (e.g., between 1 and 5 seconds)
    wait_time = between(1, 5)

    # Define tasks
    @task
    def index(self):
        self.client.get("/", verify=CERT_PATH)

    @task
    def accessibility(self):
        self.client.get("/accessibility", verify=CERT_PATH)

    @task
    def terms_of_use(self):
        self.client.get("/terms-of-use", verify=CERT_PATH)

    @task
    def how_to_use(self):
        self.client.get("/how-to-use-this-service", verify=CERT_PATH)

    @task
    def privacy(self):
        self.client.get("/privacy", verify=CERT_PATH)

    @task
    def cookies(self):
        self.client.get("/cookies", verify=CERT_PATH)


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
            headers = {"Authorization": f"Bearer {self.token}"}

            urls = [
                "/browse/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50",
                "/browse/series/1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7",
                "/browse/consignment/016031db-1398-4fe4-b743-630aa82ea32a",
                """/browse/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50?sort=
                series-asc&series_filter=TSTA&date_from_day=&date_from_month=&date_from_year
                =&date_to_day=&date_to_month=&date_to_year=#browse-records""",
                "/record/ea8a6ad6-5362-4346-a86d-22a52b9fc0c5#record-view",
                "/record/ea8a6ad6-5362-4346-a86d-22a52b9fc0c5#record-details",
            ]

            # Use secrets.choice for cryptographic randomness
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
