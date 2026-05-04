# Быстрые команды для запуска

run_django:
	uv run python manage.py runserver

run_fastapi:
	uv run uvicorn search_service.app.main:app --reload --port 8001

migrate:
	uv run python manage.py migrate

migrations:
	uv run python manage.py makemigrations

shell:
	uv run python manage.py shell

superuser:
	uv run python manage.py createsuperuser

load_genres:
	uv run python manage.py loaddata genres.json

reset_db:
	rm db.sqlite3
	uv run python manage.py migrate
	uv run python manage.py loaddata genres.json