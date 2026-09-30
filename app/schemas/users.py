from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import ORMModel, SUPPORTED_CURRENCIES, SUPPORTED_LANGUAGES, USER_ROLES


class UserBase(ORMModel):
    marina_id: int | None = None
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    role: str = "customer"
    phone: str | None = None
    language_preference: str = "en"
    currency_preference: str = "EUR"
    is_active: bool = True

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in USER_ROLES:
            raise ValueError("Unsupported role")
        return value

    @field_validator("language_preference")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in SUPPORTED_LANGUAGES:
            raise ValueError("Unsupported language")
        return value

    @field_validator("currency_preference")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if value not in SUPPORTED_CURRENCIES:
            raise ValueError("Unsupported currency")
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(ORMModel):
    marina_id: int | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = None
    language_preference: str | None = None
    currency_preference: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime
