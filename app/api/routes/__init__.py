"""API Routes Package"""
from fastapi import APIRouter
from app.api.routes import users, items, auth, documents, policies, agents

api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(agents.router, prefix="/agents", tags=["ai-agents"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
