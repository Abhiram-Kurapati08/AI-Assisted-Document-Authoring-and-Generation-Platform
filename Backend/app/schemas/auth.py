from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    hashed_password: str
