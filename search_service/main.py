from fastapi import FastAPI
from search_service.api.router import api_router
from fastapi.responses import RedirectResponse
from search_service.schemas.auth import RootResponse

app = FastAPI(title="Search service")

app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_model=RootResponse, tags=["Root"])
async def root():
    return {
        "message": 'Добро пожаловать в онлайн-кинотеатр "Джанго Освобожденный"',
        "version": "1.0.0",
        "docs_url": "/docs",
    }