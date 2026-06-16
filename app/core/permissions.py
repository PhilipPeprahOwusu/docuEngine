"""Role-Based Access Control (RBAC) Permissions"""
from functools import wraps
from fastapi import HTTPException, status
from app.models.user import User


# Role definitions
class Role:
    """Role constants for the 2-role RBAC system"""
    REVIEWER = "reviewer"
    APPROVER = "approver"

    # Legacy role mappings (for backwards compatibility during migration)
    VIEWER = "viewer"  # Maps to REVIEWER
    ADMIN = "admin"    # Maps to APPROVER

    @classmethod
    def is_approver(cls, role: str) -> bool:
        """Check if a role has approver privileges"""
        return role in [cls.APPROVER, cls.ADMIN]

    @classmethod
    def is_reviewer(cls, role: str) -> bool:
        """Check if a role has reviewer privileges (all roles can review)"""
        return role in [cls.REVIEWER, cls.APPROVER, cls.VIEWER, cls.ADMIN]

    @classmethod
    def normalize_role(cls, role: str) -> str:
        """Normalize legacy roles to the new 2-role system"""
        if role in [cls.ADMIN, cls.APPROVER]:
            return cls.APPROVER
        return cls.REVIEWER


class Permission:
    """Permission definitions for the RBAC system"""

    # Document permissions
    VIEW_CONTRACTS = "view_contracts"
    UPLOAD_CONTRACTS = "upload_contracts"
    RUN_AGENTS = "run_agents"
    EVALUATE_POLICIES = "evaluate_policies"
    VIEW_VIOLATIONS = "view_violations"
    ADD_CONTEXT = "add_context"
    REQUEST_EXCEPTION = "request_exception"

    # Approver-only permissions
    APPROVE_EXCEPTION = "approve_exception"
    REJECT_EXCEPTION = "reject_exception"
    FINALIZE_CONTRACT = "finalize_contract"

    @classmethod
    def has_permission(cls, user: User, permission: str) -> bool:
        """Check if a user has a specific permission"""
        role = user.role

        # Approver permissions (restricted)
        approver_permissions = [
            cls.APPROVE_EXCEPTION,
            cls.REJECT_EXCEPTION,
            cls.FINALIZE_CONTRACT
        ]

        if permission in approver_permissions:
            return Role.is_approver(role)

        # Reviewer permissions (all users have these)
        return Role.is_reviewer(role)


def require_approver(func):
    """
    Decorator to restrict endpoint access to Approvers only.

    Usage:
        @router.post("/finalize")
        @require_approver
        async def finalize_contract(current_user: User = Depends(get_current_user)):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current_user from kwargs
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if not Role.is_approver(current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Approvers can perform this action"
            )

        return await func(*args, **kwargs)

    return wrapper


def require_permission(permission: str):
    """
    Decorator to restrict endpoint access based on permission.

    Usage:
        @router.post("/approve")
        @require_permission(Permission.APPROVE_EXCEPTION)
        async def approve_exception(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not Permission.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You do not have permission to perform this action"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
