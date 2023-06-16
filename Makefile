up:
	docker-compose up --remove-orphans
tests:
	poetry run python -m tox run-parallel

server:
	poetry run python manage.py runserver 0.0.0.0:8000

run: server

makemigrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

shell:
	poetry run python manage.py shell
