from fastapi import FastAPI, Request
from search_service.api.router import api_router
from fastapi.responses import RedirectResponse, JSONResponse
from search_service.schemas.auth import RootResponse
from search_service.core.logger import logger

app = FastAPI(title="Search service")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """логируем все необработанные ошибки"""
    logger.error(f"непредвиденная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "внутренняя ошибка сервера"}
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_model=RootResponse, tags=["Root"])
async def root():
    return {
        "message": 'Добро пожаловать в онлайн-кинотеатр "Джанго Освобожденный"',
        "version": "1.0.0",
        "docs_url": "/docs",
    }