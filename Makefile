ENV_FILE = .docker.env
WEBAPP_POSTGRES_CA = local_services/webapp_postgres_certs/root-ca.pem
OPENSEARCH_CA = local_services/opensearch_certs/root-ca.pem
KEYCLOAK_CERT = local_services/keycloak_certs/cert.pem
RUSTFS_CA = local_services/rustfs_certs/root-ca.crt

COMPOSE = docker compose --env-file $(ENV_FILE) -f docker-compose.yml
TEST_COMPOSE = docker compose -f docker-compose.test.yml
DRI_TO_AYR_TEST_IMAGE = ayr-dri-to-ayr-migration-tests:local

.PHONY: setup start stop clean unit test test-dri-to-ayr build-dri-to-ayr-tests pre-commit e2e build-e2e-tests run-e2e-tests

$(ENV_FILE):
	cp .docker.env.template $(ENV_FILE)

$(WEBAPP_POSTGRES_CA):
	cd local_services/webapp_postgres_certs && sh ./generate_webapp_postgres_certs.sh

$(OPENSEARCH_CA):
	cd local_services/opensearch_certs && sh ./generate_opensearch_certs.sh

$(KEYCLOAK_CERT):
	sh ./local_services/generate-keycloak-certs.sh

$(RUSTFS_CA):
	cd local_services/rustfs_certs && sh ./generate_rustfs_certs.sh

setup: $(ENV_FILE) $(WEBAPP_POSTGRES_CA) $(OPENSEARCH_CA) $(KEYCLOAK_CERT) $(RUSTFS_CA)
	$(COMPOSE) build webapp

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down -v

clean:
	docker system prune -fa

test:
	poetry install --with dev --no-interaction
	AWS_DEFAULT_REGION=eu-west-2 poetry run python -m pytest --cov=app --cov-report=term-missing --cov-branch -vvv app/tests

test-dri-to-ayr:
	@docker image inspect $(DRI_TO_AYR_TEST_IMAGE) >/dev/null 2>&1 || $(TEST_COMPOSE) build dri_to_ayr_data_migration_tests
	$(TEST_COMPOSE) run --rm dri_to_ayr_data_migration_tests

build-dri-to-ayr-tests:
	$(TEST_COMPOSE) build dri_to_ayr_data_migration_tests

build-e2e-tests:
	docker build -t e2e_tests ./e2e_tests

run-e2e-tests:
	docker run --rm --env-file .env.e2e_tests --network=host -v "$(PWD)/e2e_tests":/e2e_tests -e BROWSERS=chromium,firefox,webkit e2e_tests

e2e: build-e2e-tests run-e2e-tests

pre-commit:
	poetry install --with dev --no-interaction
	poetry run pre-commit run --all-files
