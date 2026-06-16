"""Approvals and Finalization Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.policy_exception import PolicyException
from app.models.document import Document
from app.models.policy_violation import PolicyViolation
from app.core.security import oauth2_scheme, decode_access_token
from app.core.permissions import require_approver, Permission, Role
from app.services.finalization_service import FinalizationService
from app.services.notification_service import NotificationService

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


# Request/Response Models
class ExceptionRequest(BaseModel):
    """Request model for creating a policy exception"""
    document_id: str
    policy_id: str
    violation_id: str
    exception_reason: str
    valid_until: Optional[date] = None


class ApprovalDecision(BaseModel):
    """Request model for approving/rejecting an exception"""
    decision: str  # "approve" or "reject"
    rejection_reason: Optional[str] = None


class ExceptionResponse(BaseModel):
    """Response model for policy exception"""
    exception_id: str
    document_id: str
    policy_id: str
    status: str
    exception_reason: str
    requested_by: str
    requester_name: str
    approved_by: Optional[str] = None
    approver_name: Optional[str] = None
    approval_timestamp: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: str


class FinalizationResponse(BaseModel):
    """Response model for contract finalization"""
    document_id: str
    status: str
    finalized_by: str
    finalized_at: str
    signature_hash: str
    pdf_url: str
    compliance_score: float


# Exception Request Routes
@router.post("/exceptions/request", status_code=status.HTTP_201_CREATED)
async def request_exception(
    request: ExceptionRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Request a policy exception (available to all users: Reviewers and Approvers).

    Creates a pending exception request and notifies Approvers.
    """
    # Verify document exists and belongs to user's org
    document = db.query(Document).filter(
        Document.document_id == request.document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Create the exception request
    exception = PolicyException(
        exception_id=uuid.uuid4(),
        document_id=request.document_id,
        policy_id=request.policy_id,
        violation_id=request.violation_id,
        org_id=current_user.org_id,
        exception_reason=request.exception_reason,
        status="pending",
        requested_by=current_user.user_id,
        valid_until=request.valid_until,
    )

    db.add(exception)
    db.commit()
    db.refresh(exception)

    # Send notification to approvers
    notification_service = NotificationService(db_session=db)
    notification_service.send_exception_approval(
        exception_id=str(exception.exception_id),
        violations=[],  # Would fetch actual violation data
        custom_context=request.exception_reason,
        org_id=str(current_user.org_id)
    )

    return {
        "exception_id": str(exception.exception_id),
        "status": "pending",
        "message": "Exception request submitted. Approvers have been notified."
    }


# Approvals List Routes (Role-Based Views)
@router.get("/exceptions/pending", response_model=List[ExceptionResponse])
async def list_pending_approvals(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    List pending approval requests.

    - Approvers: See all pending exceptions across the organization
    - Reviewers: See their own submitted exception requests
    """
    if Role.is_approver(current_user.role):
        # Approver view: all pending exceptions in the organization
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.status == "pending"
        ).order_by(PolicyException.created_at.desc()).all()
    else:
        # Reviewer view: only their own pending requests
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.requested_by == current_user.user_id,
            PolicyException.status == "pending"
        ).order_by(PolicyException.created_at.desc()).all()

    # Format response with user names
    result = []
    for exc in exceptions:
        requester = db.query(User).filter(User.user_id == exc.requested_by).first()
        result.append({
            "exception_id": str(exc.exception_id),
            "document_id": str(exc.document_id),
            "policy_id": str(exc.policy_id),
            "status": exc.status,
            "exception_reason": exc.exception_reason,
            "requested_by": str(exc.requested_by),
            "requester_name": requester.name if requester else "Unknown",
            "approved_by": None,
            "approver_name": None,
            "approval_timestamp": None,
            "rejection_reason": None,
            "created_at": exc.created_at.isoformat()
        })

    return result


@router.get("/exceptions/approved", response_model=List[ExceptionResponse])
async def list_approved_exceptions(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """List approved exception requests (filtered by user role)"""
    if Role.is_approver(current_user.role):
        # Approver view: all approved exceptions
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.status == "approved"
        ).order_by(PolicyException.approval_timestamp.desc()).all()
    else:
        # Reviewer view: only their own approved requests
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.requested_by == current_user.user_id,
            PolicyException.status == "approved"
        ).order_by(PolicyException.approval_timestamp.desc()).all()

    result = []
    for exc in exceptions:
        requester = db.query(User).filter(User.user_id == exc.requested_by).first()
        approver = db.query(User).filter(User.user_id == exc.approved_by).first() if exc.approved_by else None

        result.append({
            "exception_id": str(exc.exception_id),
            "document_id": str(exc.document_id),
            "policy_id": str(exc.policy_id),
            "status": exc.status,
            "exception_reason": exc.exception_reason,
            "requested_by": str(exc.requested_by),
            "requester_name": requester.name if requester else "Unknown",
            "approved_by": str(exc.approved_by) if exc.approved_by else None,
            "approver_name": approver.name if approver else None,
            "approval_timestamp": exc.approval_timestamp.isoformat() if exc.approval_timestamp else None,
            "rejection_reason": None,
            "created_at": exc.created_at.isoformat()
        })

    return result


@router.get("/exceptions/rejected", response_model=List[ExceptionResponse])
async def list_rejected_exceptions(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """List rejected exception requests (filtered by user role)"""
    if Role.is_approver(current_user.role):
        # Approver view: all rejected exceptions
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.status == "rejected"
        ).order_by(PolicyException.approval_timestamp.desc()).all()
    else:
        # Reviewer view: only their own rejected requests
        exceptions = db.query(PolicyException).filter(
            PolicyException.org_id == current_user.org_id,
            PolicyException.requested_by == current_user.user_id,
            PolicyException.status == "rejected"
        ).order_by(PolicyException.approval_timestamp.desc()).all()

    result = []
    for exc in exceptions:
        requester = db.query(User).filter(User.user_id == exc.requested_by).first()
        approver = db.query(User).filter(User.user_id == exc.approved_by).first() if exc.approved_by else None

        result.append({
            "exception_id": str(exc.exception_id),
            "document_id": str(exc.document_id),
            "policy_id": str(exc.policy_id),
            "status": exc.status,
            "exception_reason": exc.exception_reason,
            "requested_by": str(exc.requested_by),
            "requester_name": requester.name if requester else "Unknown",
            "approved_by": str(exc.approved_by) if exc.approved_by else None,
            "approver_name": approver.name if approver else None,
            "approval_timestamp": exc.approval_timestamp.isoformat() if exc.approval_timestamp else None,
            "rejection_reason": exc.rejection_reason,
            "created_at": exc.created_at.isoformat()
        })

    return result


# Approval/Rejection Routes (Approver-Only)
@router.post("/exceptions/{exception_id}/approve")
async def approve_exception(
    exception_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Approve a policy exception (Approver-only).
    """
    # Check permission
    if not Role.is_approver(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Approvers can approve exceptions"
        )

    # Get the exception
    exception = db.query(PolicyException).filter(
        PolicyException.exception_id == exception_id,
        PolicyException.org_id == current_user.org_id
    ).first()

    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")

    if exception.status != "pending":
        raise HTTPException(status_code=400, detail=f"Exception is already {exception.status}")

    # Approve the exception
    exception.status = "approved"
    exception.approved_by = current_user.user_id
    exception.approval_timestamp = datetime.utcnow()

    db.commit()
    db.refresh(exception)

    return {
        "exception_id": str(exception.exception_id),
        "status": "approved",
        "approved_by": current_user.name,
        "approval_timestamp": exception.approval_timestamp.isoformat()
    }


@router.post("/exceptions/{exception_id}/reject")
async def reject_exception(
    exception_id: str,
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Reject a policy exception (Approver-only).
    """
    # Check permission
    if not Role.is_approver(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Approvers can reject exceptions"
        )

    # Get the exception
    exception = db.query(PolicyException).filter(
        PolicyException.exception_id == exception_id,
        PolicyException.org_id == current_user.org_id
    ).first()

    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")

    if exception.status != "pending":
        raise HTTPException(status_code=400, detail=f"Exception is already {exception.status}")

    # Reject the exception
    exception.status = "rejected"
    exception.approved_by = current_user.user_id
    exception.approval_timestamp = datetime.utcnow()
    exception.rejection_reason = decision.rejection_reason

    db.commit()
    db.refresh(exception)

    return {
        "exception_id": str(exception.exception_id),
        "status": "rejected",
        "rejected_by": current_user.name,
        "rejection_reason": exception.rejection_reason,
        "rejection_timestamp": exception.approval_timestamp.isoformat()
    }


# Finalization Route (Approver-Only)
@router.post("/documents/{document_id}/finalize", response_model=FinalizationResponse)
async def finalize_contract(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Finalize a contract (Approver-only).

    This endpoint:
    - Verifies all exceptions are approved
    - Generates a digital signature
    - Creates a locked PDF
    - Updates contract status to "active"
    - Sends notifications to Approver and Reviewer
    - Creates audit log entry
    """
    # Check permission
    if not Role.is_approver(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Approvers can finalize contracts"
        )

    # Verify document exists and belongs to user's org
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status == "active":
        raise HTTPException(status_code=400, detail="Document is already finalized")

    # Run finalization workflow
    try:
        finalization_service = FinalizationService(db)
        result = finalization_service.finalize_contract(
            document_id=document_id,
            approver=current_user
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")


# Download Finalized PDF
@router.get("/documents/{document_id}/pdf")
async def download_finalized_pdf(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Download the finalized locked PDF for a contract"""
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.final_pdf_url:
        raise HTTPException(status_code=404, detail="Finalized PDF not available")

    return {
        "document_id": str(document.document_id),
        "pdf_url": document.final_pdf_url,
        "filename": f"{document.filename}_finalized.pdf"
    }
