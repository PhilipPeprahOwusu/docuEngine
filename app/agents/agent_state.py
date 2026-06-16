"""Agent State Definitions for LangGraph"""
from typing import TypedDict, Annotated, Optional, List, Dict, Any
import operator


class DocumentMetadata(TypedDict):
    """Document metadata structure"""
    document_id: str
    filename: str
    parties: List[str]
    content: str
    s3_key: Optional[str]


class ExtractionResult(TypedDict):
    """Document extraction result structure"""
    parties: List[str]
    dates: Dict[str, Any]
    amounts: Dict[str, Any]
    key_terms: Dict[str, Any]


class PolicyViolation(TypedDict):
    """Policy violation structure with full citations"""
    violation_id: str
    policy_id: str
    policy_name: str
    policy_version: str
    policy_section: str
    policy_page: Optional[int]
    policy_quote: str
    document_section: str
    violation_text: str
    violation_page: Optional[int]
    severity: str
    violation_type: str
    impact: str


class AgentState(TypedDict):
    """Complete agent state for all workflows"""

    # Input
    document_id: Optional[str]
    document_a_id: Optional[str]
    document_b_id: Optional[str]
    query: Optional[str]
    custom_context: Optional[str]
    org_id: Optional[str]

    # Document data
    document: Optional[DocumentMetadata]
    document_a: Optional[DocumentMetadata]
    document_b: Optional[DocumentMetadata]

    # Extracted data
    extraction: Optional[ExtractionResult]
    extraction_a: Optional[ExtractionResult]
    extraction_b: Optional[ExtractionResult]

    # Policy evaluation
    policy_violations: Annotated[List[PolicyViolation], operator.add]
    compliance_score: Optional[float]

    # Comparison
    differences: Optional[Dict[str, Any]]
    new_in_b: Optional[List[str]]
    missing_in_b: Optional[List[str]]

    # Context & validation
    contradictions: Annotated[List[str], operator.add]
    approval_required: bool
    approval_status: Optional[str]  # pending, approved, rejected
    exception_id: Optional[str]

    # Q&A
    answer: Optional[str]
    sources: Optional[List[Dict[str, Any]]]

    # Risk assessment
    risks: Optional[Dict[str, Any]]

    # Negotiation
    recommendations: Optional[str]
    counter_offers: Optional[List[Dict[str, Any]]]

    # Metadata
    agent_name: str
    execution_start_time: Optional[float]
    execution_duration_ms: Optional[int]
    step_count: int
    error: Optional[str]
