"""AI Agent Routes"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.core.security import oauth2_scheme, decode_access_token
from app.agents.extract_agent import ExtractAgent
from app.agents.risk_agent import RiskAgent
from app.agents.qa_agent import QAAgent
from app.agents.comparison_agent import ComparisonAgent

router = APIRouter()


class CompareRequest(BaseModel):
    document_a_id: str
    document_b_id: str


class QARequest(BaseModel):
    question: str


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token_data = decode_access_token(token)
    if not token_data or not token_data.sub:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/extract/{document_id}")
async def extract_information(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Extract structured information from a document using AI"""
    # Verify document belongs to user's org
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Initialize and run extract agent with org-specific API keys
        from app.core.llm import get_llm
        llm = get_llm(db=db, org_id=str(current_user.org_id))
        agent = ExtractAgent(llm=llm, db_session=db)
        result = agent.invoke({"document_id": document_id})

        return {
            "document_id": document_id,
            "filename": document.filename,
            "extraction": result.get("extraction", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/risk/{document_id}")
async def assess_risk(
    document_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Assess risks in a document using AI"""
    # Verify document belongs to user's org
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Initialize and run risk agent with org-specific API keys
        from app.core.llm import get_llm
        llm = get_llm(db=db, org_id=str(current_user.org_id))
        agent = RiskAgent(llm=llm, db_session=db)
        result = agent.invoke({"document_id": document_id})

        return {
            "document_id": document_id,
            "filename": document.filename,
            "risks": result.get("risks", {}),
            "compliance_score": result.get("compliance_score", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/compare")
async def compare_documents(
    request: CompareRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Compare two documents using AI"""
    # Verify both documents belong to user's org
    doc_a = db.query(Document).filter(
        Document.document_id == request.document_a_id,
        Document.org_id == current_user.org_id
    ).first()

    doc_b = db.query(Document).filter(
        Document.document_id == request.document_b_id,
        Document.org_id == current_user.org_id
    ).first()

    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both documents not found")

    try:
        # Initialize and run comparison agent with org-specific API keys
        from app.core.llm import get_llm
        llm = get_llm(db=db, org_id=str(current_user.org_id))
        agent = ComparisonAgent(llm=llm, db_session=db)
        result = agent.invoke({
            "document_a_id": request.document_a_id,
            "document_b_id": request.document_b_id
        })

        return {
            "document_a": {"id": request.document_a_id, "filename": doc_a.filename},
            "document_b": {"id": request.document_b_id, "filename": doc_b.filename},
            "comparison": {
                "differences": result.get("differences", {}),
                "new_in_b": result.get("new_in_b", []),
                "missing_in_b": result.get("missing_in_b", []),
                "recommendations": result.get("recommendations", "")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/qa/{document_id}")
async def ask_question(
    document_id: str,
    request: QARequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Ask a question about a document using AI"""
    # Verify document belongs to user's org
    document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.org_id == current_user.org_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Initialize and run QA agent with org-specific API keys
        from app.core.llm import get_llm
        llm = get_llm(db=db, org_id=str(current_user.org_id))
        agent = QAAgent(llm=llm, db_session=db)
        result = agent.invoke({
            "document_id": document_id,
            "query": request.question
        })

        return {
            "document_id": document_id,
            "filename": document.filename,
            "question": request.question,
            "answer": result.get("answer", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")
