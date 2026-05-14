from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from search_service.api.v1.auth import router as auth
from search_service.core.database import get_db
from search_service.core.security import get_current_user
from search_service.models.movie import MovieModel
from search_service.schemas.movie import MovieNotify, SearchResponse
from search_service.core.logger import logger

api_router = APIRouter()

api_router.include_router(auth, prefix="/auth", tags=["Authentication"])


async def save_search_history(user_id: int, query: str):
    logger.info(f"юзер {user_id} искал '{query}'")


@api_router.post("/movies/notify", status_code=200, tags=["Movies"])
async def notify_new_movie(movie: MovieNotify):
    logger.info(f"получено уведомление о новом фильме: '{movie.title}' (ID: {movie.id})")
    return {"status": "ok", "message": "уведомление принято"}


@api_router.get("/search", response_model=SearchResponse, tags=["Search"])
async def search(
        query: str = Query(..., min_length=1, description="Строка для поиска фильма"),
        background_tasks: BackgroundTasks = BackgroundTasks(),
        session: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    stmt = select(MovieModel).where(MovieModel.title.icontains(query)).limit(20)
    result = await session.execute(stmt)
    movies_db = result.scalars().all()

    background_tasks.add_task(save_search_history, user_id=current_user.id, query=query)

    return {
        "query": query,
        "results": [
            {"id": m.id, "title": m.title, "release_year": m.release_year, "summary": m.summary}
            for m in movies_db
        ],
    }
