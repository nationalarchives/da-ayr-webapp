.PHONY: build down migrate

build:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

migrations:
	docker compose exec web python manage.py makemigrations

requirements:
	pip-compile -o requirements.txt pyproject.toml

requirements-dev:
	pip-compile --extra dev -o requirements-dev.txt pyproject.toml
