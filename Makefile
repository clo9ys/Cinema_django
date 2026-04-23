# Быстрые команды для запуска

run:
	uv run python manage.py runserver

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