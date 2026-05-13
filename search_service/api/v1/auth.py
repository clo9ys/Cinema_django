from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from search_service.core.database import get_db
from search_service.core.security import create_access_token, verify_password, get_current_user
from search_service.models.user import User
from search_service.schemas.auth import Token, UserRead
from search_service.core.logger import logger

router = APIRouter()

FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57Rw6S.XW2ny", # пароль: admin
    }
}

@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {"description": "Успешная авторизация"},
        401: {"description": "Неверный пароль"},
        404: {"description": "Пользователь не найден"},
    },
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if not user:
        logger.warning(f"ошибка входа: пользователь {form_data.username} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if not verify_password(form_data.password, user.password):
        logger.warning(f"ошибка входа: неверный пароль для пользователя {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"пользователь {user.username} успешно вошел в систему")

    return {
        "access_token": access_token,
        "refresh_token": "refresh-token",
        "token_type": "bearer",
    }
@router.get(
    "/me",
    response_model=UserRead,
    responses={
        200: {"description": "Текущий пользователь"},
        401: {"description": "Неавторизован"},
        404: {"description": "Пользователь не найден"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "message": "Авторизация прошла успешно",
    }