"""Agent Tool Definitions"""
from typing import List, Dict, Any, Optional
from langchain.tools import Tool
import json
import uuid
from datetime import datetime


# Tool 1: Information Extraction
def extract_document_info(document_text: str, llm=None) -> Dict[str, Any]:
    """
    Extract key information from document text.
    Returns: parties, dates, amounts, key terms
    """
    if not llm:
        # Mock for now - will use actual LLM
        return {
            "parties": ["Company A", "Company B"],
            "dates": {
                "effective": "2024-01-01",
                "expiration": "2025-01-01",
                "signing": "2023-12-15"
            },
            "amounts": {
                "amount": "$100,000",
                "currency": "USD",
                "payment_terms": "Net 30"
            },
            "key_terms": {
                "liability_cap": "$500,000",
                "termination_notice": "30 days",
                "governing_law": "Delaware"
            }
        }

    prompt = f"""You are a contract analysis AI. Extract key information from the following document and return ONLY a valid JSON object with this exact structure:

{{
  "parties": ["party1", "party2", ...],
  "dates": {{
    "effective_date": "YYYY-MM-DD or description",
    "expiration_date": "YYYY-MM-DD or description",
    "signing_date": "YYYY-MM-DD or description"
  }},
  "amounts": {{
    "contract_value": "amount and currency",
    "payment_terms": "description"
  }},
  "key_terms": {{
    "termination_notice": "description",
    "liability_cap": "description",
    "governing_law": "description",
    "renewal_terms": "description"
  }}
}}

If a field is not found in the document, use "Not specified" as the value. Do not include any markdown formatting, code blocks, or explanatory text - return ONLY the raw JSON object.

Document to analyze:
{document_text[:8000]}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        # Parse JSON
        extracted_data = json.loads(content)

        # Validate structure and add defaults if missing
        result = {
            "parties": extracted_data.get("parties", []),
            "dates": extracted_data.get("dates", {}),
            "amounts": extracted_data.get("amounts", {}),
            "key_terms": extracted_data.get("key_terms", {})
        }

        return result

    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract information using a simpler approach
        print(f"JSON decode error: {e}")
        print(f"LLM response: {response.content[:500]}")

        # Return the raw response as a single field for debugging
        return {
            "extraction_error": "Failed to parse LLM response as JSON",
            "raw_response": response.content[:1000],
            "parties": [],
            "dates": {},
            "amounts": {},
            "key_terms": {}
        }
    except Exception as e:
        print(f"Extraction error: {e}")
        return {
            "extraction_error": str(e),
            "parties": [],
            "dates": {},
            "amounts": {},
            "key_terms": {}
        }


# Tool 2: Policy Violation Check
def check_policy_violations(
    document_text: str,
    org_id: str,
    policy_engine=None
) -> List[Dict[str, Any]]:
    """
    Check if document violates company policies.
    Returns: violations with full citations
    """
    if not policy_engine:
        # Mock violation
        return [{
            "violation_id": str(uuid.uuid4()),
            "policy_id": "pol_001",
            "policy_name": "Payment Terms Policy",
            "policy_version": "1.0",
            "policy_section": "Section 2.1",
            "policy_page": 3,
            "policy_quote": "All documents must specify payment terms of Net 30 days. Maximum acceptable is Net 45 days.",
            "document_section": "Section 3.2",
            "violation_text": "Payment shall be due within 60 days of invoice date",
            "violation_page": 2,
            "severity": "HIGH",
            "violation_type": "payment_terms",
            "impact": "Extends cash flow by 15 days beyond policy limit"
        }]

    return policy_engine.evaluate(document_text, org_id)


# Tool 3: Document Comparison
def compare_documents(
    extraction_a: Dict[str, Any],
    extraction_b: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare two document extractions.
    Returns: differences, new terms, missing terms
    """
    differences = {}

    # Compare parties
    parties_a = set(extraction_a.get("parties", []))
    parties_b = set(extraction_b.get("parties", []))
    parties_diff = {
        "in_a_not_b": list(parties_a - parties_b),
        "in_b_not_a": list(parties_b - parties_a)
    }
    if any(parties_diff.values()):
        differences["parties"] = parties_diff

    # Compare dates
    dates_diff = {}
    dates_a = extraction_a.get("dates", {})
    dates_b = extraction_b.get("dates", {})
    for date_type in ["effective", "expiration", "signing"]:
        a_val = dates_a.get(date_type)
        b_val = dates_b.get(date_type)
        if a_val != b_val:
            dates_diff[date_type] = {"a": a_val, "b": b_val}
    if dates_diff:
        differences["dates"] = dates_diff

    # Compare amounts
    amounts_diff = {}
    amounts_a = extraction_a.get("amounts", {})
    amounts_b = extraction_b.get("amounts", {})
    a_amount = amounts_a.get("amount")
    b_amount = amounts_b.get("amount")
    if a_amount != b_amount:
        amounts_diff["amount"] = {"a": a_amount, "b": b_amount}
    if amounts_diff:
        differences["amounts"] = amounts_diff

    # Compare key terms
    terms_a = set(extraction_a.get("key_terms", {}).keys())
    terms_b = set(extraction_b.get("key_terms", {}).keys())

    return {
        "differences": differences,
        "new_in_b": list(terms_b - terms_a),
        "missing_in_b": list(terms_a - terms_b)
    }


# Tool 4: Risk Assessment
def assess_risks(document_text: str, llm=None) -> Dict[str, Any]:
    """
    Assess risks in document.
    Returns: risk categories with severity and compliance score
    """
    if not llm:
        # Mock risks
        return {
            "payment_obligations": {
                "description": "Payment due within 60 days with 2% late fee",
                "severity": "MEDIUM",
                "section": "Section 3.2"
            },
            "termination_clauses": {
                "description": "30 day notice required, no early termination fee",
                "severity": "LOW",
                "section": "Section 8.1"
            },
            "liability_caps": {
                "description": "Liability capped at $500,000 total",
                "severity": "HIGH",
                "section": "Section 10.3"
            }
        }

    prompt = f"""You are a legal risk assessment AI. Analyze the following document and identify potential risks. Return ONLY a valid JSON object with this structure:

{{
  "payment_obligations": {{
    "description": "description of payment risks",
    "severity": "LOW|MEDIUM|HIGH",
    "section": "section reference or 'Not specified'"
  }},
  "termination_clauses": {{
    "description": "description of termination risks",
    "severity": "LOW|MEDIUM|HIGH",
    "section": "section reference or 'Not specified'"
  }},
  "liability_caps": {{
    "description": "description of liability risks",
    "severity": "LOW|MEDIUM|HIGH",
    "section": "section reference or 'Not specified'"
  }},
  "indemnification": {{
    "description": "description of indemnification risks",
    "severity": "LOW|MEDIUM|HIGH",
    "section": "section reference or 'Not specified'"
  }},
  "compliance_requirements": {{
    "description": "description of compliance risks",
    "severity": "LOW|MEDIUM|HIGH",
    "section": "section reference or 'Not specified'"
  }}
}}

Severity levels:
- LOW: Minor issue, standard terms
- MEDIUM: Moderate concern, review recommended
- HIGH: Significant risk, requires attention

If a risk category is not applicable, set description to "Not applicable" and severity to "LOW". Do not include markdown formatting or code blocks - return ONLY the raw JSON object.

Document to analyze:
{document_text[:8000]}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        # Parse JSON
        risks = json.loads(content)

        return risks

    except json.JSONDecodeError as e:
        print(f"Risk assessment JSON decode error: {e}")
        print(f"LLM response: {response.content[:500]}")

        return {
            "extraction_error": "Failed to parse LLM response as JSON",
            "raw_response": response.content[:1000]
        }
    except Exception as e:
        print(f"Risk assessment error: {e}")
        return {
            "extraction_error": str(e)
        }


# Tool 5: Semantic Search (for Q&A)
def search_document(
    query: str,
    document_id: str,
    vector_db=None
) -> List[Dict[str, Any]]:
    """
    Semantically search document for relevant sections.
    Returns: ranked chunks with similarity scores
    """
    if not vector_db:
        # Mock search results
        return [
            {
                "text": "Payment terms are Net 60 days from invoice date.",
                "section": "Section 3.2",
                "page": 2,
                "similarity": 0.92
            },
            {
                "text": "Late payments incur a 2% monthly penalty.",
                "section": "Section 3.3",
                "page": 2,
                "similarity": 0.85
            }
        ]

    # Vector search
    results = vector_db.search(
        query=query,
        document_id=document_id,
        top_k=5
    )

    return results


# Tool 6: Validate Context Against Policies
def validate_context(
    context_text: str,
    violations: List[Dict[str, Any]],
    org_id: str,
    llm=None
) -> Dict[str, Any]:
    """
    Check if custom context contradicts policies.
    Returns: contradictions and approval requirement
    """
    if not llm:
        # Mock validation
        if "VP approved" in context_text.lower():
            return {
                "contradictions": [],
                "requires_approval": False,
                "approval_level": None
            }
        return {
            "contradictions": ["Context contradicts payment terms policy"],
            "requires_approval": True,
            "approval_level": "supervisor"
        }

    prompt = f"""
    User provided this context: "{context_text}"

    This document has these policy violations:
    {json.dumps(violations, indent=2)}

    Does the user's context contradict any of these policies?
    For each contradiction, explain why it violates the policy.

    Return JSON with:
    - contradictions: list of contradiction descriptions
    - requires_approval: boolean
    - approval_level: "supervisor" or "executive" or null
    """

    response = llm.invoke(prompt)
    try:
        result = json.loads(response.content)
        return result
    except:
        return {
            "contradictions": [],
            "requires_approval": False,
            "approval_level": None
        }


# Register all tools
def get_agent_tools(llm=None, policy_engine=None, vector_db=None) -> Dict[str, Tool]:
    """Get all available agent tools"""

    return {
        "information_extraction": Tool(
            name="extract_info",
            description="Extract parties, dates, amounts, and key terms from a document",
            func=lambda text: extract_document_info(text, llm)
        ),
        "policy_violation_check": Tool(
            name="check_violations",
            description="Check document against company policies and return violations with citations",
            func=lambda text, org_id: check_policy_violations(text, org_id, policy_engine)
        ),
        "document_comparison": Tool(
            name="compare_documents",
            description="Compare two document extractions and identify differences",
            func=compare_documents
        ),
        "risk_assessment": Tool(
            name="assess_risks",
            description="Assess and categorize risks in a document",
            func=lambda text: assess_risks(text, llm)
        ),
        "semantic_search": Tool(
            name="search_document",
            description="Semantically search a document for relevant sections based on a query",
            func=lambda query, document_id: search_document(query, document_id, vector_db)
        ),
        "validate_context": Tool(
            name="validate_context",
            description="Validate custom context against company policies",
            func=lambda context, violations, org_id: validate_context(context, violations, org_id, llm)
        )
    }
