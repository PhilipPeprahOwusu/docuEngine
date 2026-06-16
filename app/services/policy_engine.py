"""Policy Evaluation Engine with Full Citations"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime


class PolicyEvaluationEngine:
    """Evaluates contracts against company policies and generates citations"""

    def __init__(self, db_session: Session, llm=None):
        self.db = db_session
        self.llm = llm

    def evaluate_all(
        self,
        contract_text: str,
        org_id: str,
        contract_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate contract against ALL active company policies.
        Returns list of violations with full citations.
        """
        from app.models.company_policy import CompanyPolicy

        # Get all active policies for org
        policies = self.db.query(CompanyPolicy).filter(
            CompanyPolicy.org_id == org_id,
            CompanyPolicy.status == "active"
        ).all()

        all_violations = []

        for policy in policies:
            violations = self._evaluate_against_policy(
                contract_text,
                policy,
                contract_id
            )
            all_violations.extend(violations)

        return all_violations

    def _evaluate_against_policy(
        self,
        contract_text: str,
        policy,
        contract_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate contract against a single policy.
        Returns violations for this policy.
        """
        violations = []

        # Get policy rules
        policy_rules = policy.policy_rules or []

        if not isinstance(policy_rules, list):
            # If rules are stored as dict, convert
            if "rules" in policy_rules:
                policy_rules = policy_rules["rules"]
            else:
                return []

        for rule in policy_rules:
            violation = self._check_rule(contract_text, rule, policy, contract_id)
            if violation:
                violations.append(violation)

        return violations

    def _check_rule(
        self,
        contract_text: str,
        rule: Dict[str, Any],
        policy,
        contract_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if contract violates a specific policy rule.
        Returns violation dict with full citations, or None.
        """
        rule_type = rule.get("rule_type")
        requirement = rule.get("requirement")
        parameters = rule.get("parameters", {})

        # Use LLM to check for violation
        if self.llm:
            violation_check = self._llm_check_rule(
                contract_text,
                rule,
                policy
            )
        else:
            # Mock violation for testing
            violation_check = self._mock_check_rule(rule_type)

        if not violation_check or not violation_check.get("is_violation"):
            return None

        # Build full citation structure
        violation = {
            "violation_id": str(uuid.uuid4()),
            "policy_id": str(policy.policy_id),
            "policy_name": policy.policy_name,
            "policy_version": policy.version,
            "policy_section": rule.get("section", ""),
            "policy_page": rule.get("page"),
            "policy_quote": rule.get("quote", requirement),

            "contract_section": violation_check.get("contract_section", ""),
            "violation_text": violation_check.get("violation_text", ""),
            "violation_page": violation_check.get("violation_page"),
            "violation_paragraph": violation_check.get("violation_paragraph"),

            "severity": violation_check.get("severity", "MEDIUM"),
            "violation_type": rule_type,
            "policy_value": parameters.get("default_value", ""),
            "actual_value": violation_check.get("actual_value", ""),
            "difference": violation_check.get("difference", ""),
            "impact_description": violation_check.get("impact", ""),

            "detected_at": datetime.utcnow().isoformat(),
            "detected_by_agent": "policy_evaluation_engine_v1",
            "policy_version_at_detection": policy.version,
            "contract_version_at_detection": "1.0",

            "policy_document_url": f"/api/policies/{policy.policy_id}/download",
            "contract_document_url": f"/api/contracts/{contract_id}/download" if contract_id else None
        }

        return violation

    def _llm_check_rule(
        self,
        contract_text: str,
        rule: Dict[str, Any],
        policy
    ) -> Optional[Dict[str, Any]]:
        """Use LLM to check if contract violates rule"""
        prompt = f"""
        Policy Rule:
        Type: {rule.get('rule_type')}
        Requirement: {rule.get('requirement')}
        Section: {rule.get('section')}
        Quote: "{rule.get('quote')}"
        Parameters: {rule.get('parameters')}

        Contract Text (first 5000 chars):
        {contract_text[:5000]}

        Does this contract violate the policy rule?

        Return JSON:
        {{
            "is_violation": boolean,
            "contract_section": "Section X.Y",
            "violation_text": "exact quote from contract",
            "violation_page": page_number,
            "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
            "actual_value": "what the contract says",
            "difference": "how it differs from policy",
            "impact": "business impact description"
        }}
        """

        try:
            response = self.llm.invoke(prompt)
            import json
            result = json.loads(response.content)
            return result
        except Exception as e:
            print(f"LLM check failed: {e}")
            return None

    def _mock_check_rule(self, rule_type: str) -> Optional[Dict[str, Any]]:
        """Mock rule checking for testing"""
        # Simulate finding a violation for demo purposes
        if rule_type == "payment_terms":
            return {
                "is_violation": True,
                "contract_section": "Section 3.2",
                "violation_text": "Payment shall be due within 60 days of invoice date",
                "violation_page": 2,
                "severity": "HIGH",
                "actual_value": "Net 60",
                "difference": "+15 days beyond policy maximum",
                "impact": "Extends cash flow by 15 days beyond policy limit"
            }

        return None  # No violation

    def save_violations(
        self,
        violations: List[Dict[str, Any]],
        contract_id: str,
        org_id: str
    ):
        """Save violations to database"""
        from app.models.policy_violation import PolicyViolation

        for violation_data in violations:
            violation = PolicyViolation(
                violation_id=violation_data["violation_id"],
                contract_id=contract_id,
                policy_id=violation_data["policy_id"],
                org_id=org_id,
                policy_name=violation_data["policy_name"],
                policy_version=violation_data["policy_version"],
                policy_section=violation_data["policy_section"],
                policy_page=violation_data.get("policy_page"),
                policy_quote=violation_data["policy_quote"],
                contract_name=violation_data.get("contract_name", ""),
                violation_text=violation_data["violation_text"],
                violation_section=violation_data["contract_section"],
                violation_page=violation_data.get("violation_page"),
                violation_paragraph=violation_data.get("violation_paragraph"),
                severity=violation_data["severity"],
                violation_type=violation_data["violation_type"],
                policy_value=violation_data.get("policy_value"),
                actual_value=violation_data.get("actual_value"),
                difference=violation_data.get("difference"),
                impact_description=violation_data["impact_description"],
                detected_by_agent=violation_data["detected_by_agent"],
                policy_version_at_detection=violation_data["policy_version_at_detection"],
                contract_version_at_detection=violation_data.get("contract_version_at_detection"),
                policy_document_url=violation_data.get("policy_document_url"),
                contract_document_url=violation_data.get("contract_document_url")
            )

            self.db.add(violation)

        self.db.commit()

    def calculate_compliance_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate compliance score (0-100) based on violations"""
        if not violations:
            return 100.0

        # Weight by severity
        severity_weights = {
            "LOW": 5,
            "MEDIUM": 15,
            "HIGH": 25,
            "CRITICAL": 40
        }

        total_deduction = sum(
            severity_weights.get(v.get("severity", "MEDIUM"), 15)
            for v in violations
        )

        score = max(0, 100 - total_deduction)
        return round(score, 2)
