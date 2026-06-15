"""Item Routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ItemResponse])
async def get_items(skip: int = 0, limit: int = 100):
    """Get list of items"""
    # TODO: Implement get items logic
    return []


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get item by ID"""
    # TODO: Implement get item by ID logic
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item_data: ItemCreate, current_user: dict = Depends(get_current_user)):
    """Create new item"""
    # TODO: Implement create item logic
    return {"id": 1, "title": item_data.title, "description": item_data.description, "owner_id": 1}


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_data: ItemUpdate, current_user: dict = Depends(get_current_user)):
    """Update item"""
    # TODO: Implement update item logic
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, current_user: dict = Depends(get_current_user)):
    """Delete item"""
    # TODO: Implement delete item logic
    return None
