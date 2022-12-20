.PHONY: build down migrate

build:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

migrations:
	docker compose exec web python manage.py makemigrations
