from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=25, description="имя пользователя")
    email: EmailStr = Field(..., description="электронная почта")
    password: str = Field(..., min_length=8, max_length=25, description="пароль (минимум 8 символов")


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str="bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserRead(BaseModel):
    id: int = Field(..., example=1)
    username: str = Field(..., example="admin")
    email: EmailStr | None = Field(None, example="admin-cinema@gmail.com")

    class Meta:
        from_attributes = True


class RootResponse(BaseModel):
    message: str = Field(..., example="Welcome to Cinema")
    docs_url: str = Field(..., example="/docs")