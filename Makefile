up:
	docker-compose run --remove-orphans --rm --service-ports development

tests:
	poetry run python -m tox run-parallel

server:
	poetry run python manage.py runserver 0.0.0.0:8000
