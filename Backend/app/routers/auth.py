from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from .. import models, schemas
from ..database import get_db
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    - **email**: User's email address (must be unique)
    - **password**: Password (min 8 chars, must contain uppercase, lowercase, and number)
    """
    auth_service = AuthService(db)
    try:
        user = await auth_service.register_user(user_data)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        ) from e

@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Login with email and password"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: Your email address
    - **password**: Your password
    
    Returns:
    - **access_token**: JWT access token
    - **refresh_token**: JWT refresh token
    - **token_type**: Always "bearer"
    """
    auth_service = AuthService(db)
    try:
        return await auth_service.login(
            email=form_data.username,
            password=form_data.password
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        ) from e

@router.post(
    "/refresh",
    response_model=schemas.Token,
    summary="Refresh access token"
)
async def refresh_token(
    token_data: schemas.Token,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a new access token using a refresh token.
    
    - **refresh_token**: A valid refresh token
    
    Returns:
    - **access_token**: New JWT access token
    - **refresh_token**: New JWT refresh token
    - **token_type**: Always "bearer"
    """
    auth_service = AuthService(db)
    try:
        return await auth_service.refresh_tokens(token_data.refresh_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing the token"
        ) from e
