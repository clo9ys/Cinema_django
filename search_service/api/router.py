from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from search_service.api.v1.auth import router as auth
from search_service.core.database import get_db
from search_service.models.movie import MovieModel  # Наша SQLAlchemy модель
from search_service.core.logger import logger  # Твой логгер

api_router = APIRouter()

api_router.include_router(auth, prefix="/auth", tags=["Authentication"])


async def save_search_history(user_id: int, query: str):
    logger.info(f"юзер {user_id} искал '{query}'")


@api_router.get("/search")
async def search(
        query: str = Query(..., min_length=1, description="Строка для поиска фильма"),
        background_tasks: BackgroundTasks = BackgroundTasks(),
        session: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    stmt = select(MovieModel).where(MovieModel.title.icontains(query)).limit(20)
    result = await session.execute(stmt)

    movies_db = result.scalars().all()

    search_results = {
        "query": query,
        "results": [
            {
                "id": movie.id,
                "title": movie.title,
                "release_year": movie.release_year,
                "summary": movie.summary
            } for movie in movies_db
        ]
    }

    background_tasks.add_task(save_search_history, user_id=current_user.id, query=query)

    return search_results
