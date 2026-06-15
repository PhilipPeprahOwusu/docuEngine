"""Item Schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base item schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Item creation schema"""
    pass


class ItemUpdate(BaseModel):
    """Item update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class ItemResponse(ItemBase):
    """Item response schema"""
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItemInDB(ItemBase):
    """Item in database schema"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
