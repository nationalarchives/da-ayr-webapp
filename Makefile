ENV_FILE = .docker.env
WEBAPP_POSTGRES_CA = local_services/webapp_postgres_certs/root-ca.pem
OPENSEARCH_CA = local_services/opensearch_certs/root-ca.pem
KEYCLOAK_CERT = local_services/keycloak_certs/cert.pem

COMPOSE = docker compose --env-file $(ENV_FILE) -f docker-compose.yml

.PHONY: setup start stop clean unit test pre-commit e2e build-e2e-tests run-e2e-tests

$(ENV_FILE):
	cp .docker.env.template $(ENV_FILE)

$(WEBAPP_POSTGRES_CA):
	cd local_services/webapp_postgres_certs && sh ./generate_webapp_postgres_certs.sh

$(OPENSEARCH_CA):
	cd local_services/opensearch_certs && sh ./generate_opensearch_certs.sh

$(KEYCLOAK_CERT):
	sh ./local_services/generate-keycloak-certs.sh

setup: $(ENV_FILE) $(WEBAPP_POSTGRES_CA) $(OPENSEARCH_CA) $(KEYCLOAK_CERT)
	$(COMPOSE) build webapp

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down -v

clean:
	docker system prune -fa

test:
	poetry install --with dev --no-interaction
	poetry run python -m pytest --cov=app --cov-report=term-missing --cov-branch -vvv app/tests

build-e2e-tests:
	docker build -t e2e_tests ./e2e_tests

run-e2e-tests:
	docker run --rm --env-file .env.e2e_tests --network=host -v "$(PWD)/e2e_tests":/e2e_tests -e BROWSERS=webkit e2e_tests

e2e: build-e2e-tests run-e2e-tests

pre-commit:
	poetry install --with dev --no-interaction
	poetry run pre-commit run --all-files
