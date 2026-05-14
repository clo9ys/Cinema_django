from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from search_service.core.config import settings
from search_service.core.database import get_db
from search_service.core.security import (
    create_access_token, create_refresh_token,
    verify_password, hash_password, get_current_user,
)
from search_service.models.user import User
from search_service.schemas.auth import Token, UserCreate, UserRead
from search_service.core.logger import logger

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Пользователь создан"},
        409: {"description": "Имя пользователя уже занято"},
    },
)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Имя пользователя уже занято")

    user = User(username=body.username, email=body.email, password=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"зарегистрирован новый пользователь: {user.username}")
    return user


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if not verify_password(form_data.password, user.password):
        logger.warning(f"ошибка входа: неверный пароль для пользователя {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    logger.info(f"пользователь {user.username} успешно вошел в систему")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post(
    "/refresh",
    response_model=Token,
    responses={
        200: {"description": "Токены обновлены"},
        401: {"description": "Невалидный refresh token"},
    },
)
async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, settings.FASTAPI_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise credentials_exception

    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "refresh_token": create_refresh_token(data={"sub": user.username}),
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserRead,
    responses={
        200: {"description": "Текущий пользователь"},
        401: {"description": "Неавторизован"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user