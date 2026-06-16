"""User Routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/me")
async def get_current_user_info(db: Session = Depends(get_db)):
    """Get current user information"""
    from app.core.security import oauth2_scheme, decode_access_token
    from fastapi import Request

    # Get token from Authorization header
    async def get_token_from_request(request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        return auth_header.split(" ")[1]

    # This is a workaround - in production you'd use proper dependency injection
    # For now, just document that the endpoint requires Bearer token
    raise HTTPException(
        status_code=501,
        detail="Use /api/v1/users/me endpoint is not yet implemented. User info is embedded in login response."
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    # TODO: Implement get user by ID logic
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    """Update user"""
    # TODO: Implement update user logic
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete user"""
    # TODO: Implement delete user logic
    return None
