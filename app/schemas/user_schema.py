from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: UserRole
