up:
	docker-compose up --remove-orphans

tests:
	tox run-parallel -p auto

test-latest:
	tox run -e py3.11-django42

server:
	poetry run python manage.py runserver 0.0.0.0:8000

run: server

migrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

shell:
	poetry run python manage.py shell

isort:
	poetry run pre-commit run --all-files isort

black:
	poetry run pre-commit run --all-files black

pylint:
	poetry run pre-commit run --all-files pylint

bandit:
	poetry run pre-commit run --all-files bandit

mypy:
	poetry run pre-commit run --all-files mypy

lint:
	poetry run pre-commit run --all-files
