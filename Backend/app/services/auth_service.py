from datetime import timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..utils.jwt_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, user_data: schemas.UserCreate) -> models.User:
        """Register a new user."""
        # Check if user already exists
        db_user = (
            self.db.query(models.User)
            .filter(models.User.email == user_data.email)
            .first()
        )
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = models.User(
            email=user_data.email,
            password_hash=hashed_password,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Optional[models.User]:
        """Authenticate a user and return the user if successful."""
        user = (
            self.db.query(models.User)
            .filter(models.User.email == email)
            .first()
        )
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    async def login(
        self, 
        email: str, 
        password: str
    ) -> schemas.Token:
        """Authenticate user and return access and refresh tokens."""
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return schemas.Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_tokens(
        self, 
        refresh_token: str
    ) -> schemas.Token:
        """Refresh access token using a refresh token."""
        try:
            payload = await verify_token(refresh_token)
            if not payload.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create new tokens
            access_token = create_access_token(
                data={"sub": payload.user_id, "email": payload.email},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            new_refresh_token = create_refresh_token(
                data={"sub": payload.user_id, "email": payload.email},
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            
            return schemas.Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self, 
        token: str
    ) -> models.User:
        """Get the current user from a JWT token."""
        try:
            payload = await verify_token(token)
            if not payload.user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = (
                self.db.query(models.User)
                .filter(models.User.id == UUID(payload.user_id))
                .first()
            )
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_dep(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Dependency that returns the current authenticated user."""
    return await AuthService(db).get_current_user(token)
