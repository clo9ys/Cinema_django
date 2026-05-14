import httpx
from django.conf import settings
import logging

logger = logging.getLogger('cinema')

def notify_fastapi_about_new_movie(movie):
    """
    Отправляет уведомление в FastAPI (Search Service) о новом фильме.
    """
    # Предполагаем, что URL FastAPI задан в настройках, или используем дефолтный
    fastapi_url = getattr(settings, "FASTAPI_SEARCH_SERVICE_URL", "http://localhost:8000")
    endpoint = f"{fastapi_url}/api/v1/movies/notify"
    
    payload = {
        "id": movie.id,
        "title": movie.title,
        "release_year": movie.release_year,
        "summary": movie.summary,
        "duration_minutes": movie.duration_minutes,
        "age_limit": movie.age_limit,
    }
    
    try:
        # Используем таймаут, чтобы не блокировать админку при недоступности FastAPI
        response = httpx.post(endpoint, json=payload, timeout=2.0)
        response.raise_for_status()
        logger.info(f"Успешно отправлено уведомление в FastAPI о фильме '{movie.title}'")
    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при отправке уведомления в FastAPI о фильме '{movie.title}': {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"FastAPI вернул ошибку {e.response.status_code} при уведомлении о фильме '{movie.title}'")
