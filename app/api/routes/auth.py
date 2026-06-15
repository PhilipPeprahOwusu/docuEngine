"""Authentication Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token, TokenData
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    # TODO: Implement user registration logic
    return {"id": 1, "email": user_data.email, "username": user_data.username, "is_active": True}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    # TODO: Implement login logic
    return {
        "access_token": "sample_token",
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token():
    """Refresh access token"""
    # TODO: Implement token refresh logic
    return {
        "access_token": "new_sample_token",
        "token_type": "bearer"
    }
