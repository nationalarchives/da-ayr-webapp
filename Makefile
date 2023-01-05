.PHONY: all help clean up down test pytest flake8 rm-test migrate migrations requirements requirements-dev


SHELL = /bin/bash
COMPOSE ?= docker compose
GIT ?= git
APP_NAME = da-ayr-webapp
TEST_NAME = da-ayr-webapp-test
TEST_TAG = $(TEST_NAME):latest

all: help

help:
	@echo "test	                     - Run unit tests in Docker container."
	@echo "up                        - Docker compose build and up."
	@echo "down                      - Docker compose down"
	@echo "migrate                   - Run migrations"
	@echo "migrations                - Create migrations"
	@echo "requirements              - Generate requirements file"
	@echo "requirements-dev          - Generate requirements-dev file"

clean:
	rm -fr *.egg-info **/__pycache__ dist build **/.pytest_cache **/.coverage
	rm -f *.un~ **/*.un~ .*.un~ **/.*.un~
	rm -f **/.DS_Store
	rm -f **/*.pyc
	rm -fr .coverage
	rm -fr .pytest_cache


build_latest:
	docker build --target=release -t $(APP_NAME):latest .

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

test:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . && docker run --env-file .env --rm $(TEST_NAME) bash tests.sh

pytest:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . && docker run --env-file .env --rm $(TEST_NAME) pytest -s

flake8:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . && docker run --env-file .env --rm $(TEST_NAME) flake8 app project tests

rm-test:
	docker container rm $(TEST_NAME)

black:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . &&\
 	docker run --name=$(TEST_NAME) $(TEST_NAME) black . &&\
	docker cp $(TEST_NAME):/code/. ./

migrate:
	$(COMPOSE) up web -d && $(COMPOSE) exec web python manage.py migrate

migrations:
	$(COMPOSE) up web -d && $(COMPOSE) exec web python manage.py makemigrations

requirements:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . &&\
 	docker run --name=$(TEST_NAME) $(TEST_NAME) pip-compile -o requirements.txt pyproject.toml &&\
 	docker cp $(TEST_NAME):/code/requirements.txt ./requirements.txt

requirements-dev:
	docker container rm $(TEST_NAME) || true &&\
	docker build --target=test -t $(TEST_TAG) . &&\
 	docker run --name=$(TEST_NAME) $(TEST_NAME) pip-compile --extra dev -o requirements-dev.txt pyproject.toml &&\
 	docker cp $(TEST_NAME):/code/requirements-dev.txt ./requirements-dev.txt
