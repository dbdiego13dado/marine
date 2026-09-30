from pydantic import BaseModel, EmailStr, Field

from app.schemas.users import UserRead


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    marina_id: int | None = None
    phone: str | None = None
    language_preference: str = "en"
    currency_preference: str = "EUR"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    message: str
    user: UserRead
