"""Policy Routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.company_policy import CompanyPolicy
from app.models.user import User
from app.core.security import oauth2_scheme, decode_access_token

router = APIRouter()


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token_data = decode_access_token(token)
    if not token_data or not token_data.sub:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/")
async def list_policies(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all policies for the current user's organization"""
    policies = db.query(CompanyPolicy).filter(
        CompanyPolicy.org_id == current_user.org_id
    ).order_by(CompanyPolicy.created_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": str(policy.policy_id),
        "name": policy.policy_name,
        "description": policy.policy_description,
        "status": policy.status,
        "version": policy.version,
        "created_at": policy.created_at.isoformat(),
    } for policy in policies]


@router.post("/")
async def create_policy(
    policy_name: str,
    policy_description: str,
    policy_document: str,
    version: str = "1.0",
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Create a new policy"""
    import uuid

    new_policy = CompanyPolicy(
        policy_id=uuid.uuid4(),
        org_id=current_user.org_id,
        policy_name=policy_name,
        policy_description=policy_description,
        policy_document=policy_document,
        version=version,
        status="active",
        created_by=current_user.user_id
    )

    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    return {
        "id": str(new_policy.policy_id),
        "name": new_policy.policy_name,
        "description": new_policy.policy_description,
        "version": new_policy.version,
        "status": new_policy.status,
    }


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete a policy"""
    policy = db.query(CompanyPolicy).filter(
        CompanyPolicy.policy_id == policy_id,
        CompanyPolicy.org_id == current_user.org_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.delete(policy)
    db.commit()

    return {"message": "Policy deleted successfully"}
