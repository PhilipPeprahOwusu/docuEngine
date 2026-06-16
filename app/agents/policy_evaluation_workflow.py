"""Policy Evaluation Workflow with Human-in-the-Loop Approval"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from typing import Dict, Any
import uuid
from datetime import datetime


class PolicyEvaluationWorkflow(BaseAgentGraph):
    """
    Evaluates documents against policies with supervisor approval workflow.

    Flow:
    1. Load document + policies
    2. Evaluate against all policies
    3. If violations → wait for user context
    4. Validate context against policies
    5. If contradiction → wait for supervisor approval
    6. Save results
    """

    def __init__(self, llm=None, db_session=None, policy_engine=None, notification_service=None):
        super().__init__("policy_evaluation_workflow", llm)
        self.db = db_session
        self.policy_engine = policy_engine
        self.notification_service = notification_service

        # NODE 1: Load document and policies
        def load_document_and_policies(state: Dict[str, Any]) -> Dict[str, Any]:
            """Load document from database"""
            from app.models.document import Document

            if not self.db:
                return {
                    "document": {
                        "document_id": state["document_id"],
                        "content": "Mock document content...",
                        "filename": "test.pdf"
                    }
                }

            document = self.db.query(Document).filter(
                Document.document_id == state["document_id"]
            ).first()

            if not document:
                return {"error": f"Document {state['document_id']} not found"}

            return {
                "document": {
                    "document_id": str(document.document_id),
                    "content": document.content,
                    "filename": document.filename
                }
            }

        # NODE 2: Evaluate against policies
        def evaluate_policies(state: Dict[str, Any]) -> Dict[str, Any]:
            """Run policy evaluation engine"""
            if not self.policy_engine:
                # Mock violation
                violations = [{
                    "violation_id": str(uuid.uuid4()),
                    "policy_id": "pol_001",
                    "policy_name": "Payment Terms Policy",
                    "severity": "HIGH",
                    "impact_description": "Violates payment terms",
                    "policy_quote": "Net 30 maximum",
                    "violation_text": "Net 60 specified"
                }]
            else:
                violations = self.policy_engine.evaluate_all(
                    document_text=state["document"]["content"],
                    org_id=state["org_id"],
                    document_id=state["document_id"]
                )

            compliance_score = self._calculate_score(violations)

            return {
                "policy_violations": violations,
                "compliance_score": compliance_score
            }

        # NODE 3: Wait for user context (PAUSE POINT)
        def wait_for_context(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Pause here - user will add context via API.
            Workflow resumes when context is provided.
            """
            # This is a pause point - workflow will wait
            # User calls API to add context, which resumes workflow
            return {}

        # NODE 4: Validate context
        def validate_context(state: Dict[str, Any]) -> Dict[str, Any]:
            """Check if context contradicts policies"""
            from app.agents.tools import validate_context as validate_context_tool

            if not state.get("custom_context"):
                return {
                    "contradictions": [],
                    "approval_required": False
                }

            result = validate_context_tool(
                context_text=state["custom_context"],
                violations=state["policy_violations"],
                org_id=state["org_id"],
                llm=self.llm
            )

            return {
                "contradictions": result.get("contradictions", []),
                "approval_required": result.get("requires_approval", False)
            }

        # NODE 5: Wait for approval (PAUSE POINT)
        def wait_for_approval(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Send notification to supervisor.
            Pause until approval received.
            """
            if not self.db:
                return {"exception_id": str(uuid.uuid4())}

            from app.models.policy_exception import PolicyException

            # Create exception record
            exception = PolicyException(
                exception_id=uuid.uuid4(),
                document_id=state["document_id"],
                policy_id=state["policy_violations"][0]["policy_id"] if state["policy_violations"] else None,
                org_id=state["org_id"],
                exception_reason=state.get("custom_context"),
                approved_by=None,  # Will be set on approval
                approval_timestamp=None
            )

            self.db.add(exception)
            self.db.commit()

            exception_id = str(exception.exception_id)

            # Send notification
            if self.notification_service:
                self.notification_service.send_exception_approval(
                    exception_id=exception_id,
                    violations=state["policy_violations"],
                    custom_context=state.get("custom_context"),
                    org_id=state["org_id"]
                )

            return {"exception_id": exception_id}

        # NODE 6: Save results
        def save_result(state: Dict[str, Any]) -> Dict[str, Any]:
            """Save evaluation results to database"""
            if not self.db:
                return {}

            from app.models.policy_violation import PolicyViolation

            # Save violations
            if self.policy_engine and state.get("policy_violations"):
                self.policy_engine.save_violations(
                    violations=state["policy_violations"],
                    document_id=state["document_id"],
                    org_id=state["org_id"]
                )

            return {"saved": True}

        # Routing functions
        def route_after_evaluation(state: Dict[str, Any]) -> str:
            """Route based on whether violations exist"""
            if not state.get("policy_violations"):
                return "save"
            else:
                return "wait_context"

        def route_after_validation(state: Dict[str, Any]) -> str:
            """Route based on whether approval required"""
            if state.get("approval_required"):
                return "wait_approval"
            else:
                return "save"

        # Build graph
        self.workflow.set_entry_point("load")

        self.create_node("load", load_document_and_policies)
        self.create_node("evaluate", evaluate_policies)
        self.create_node("wait_context", wait_for_context)
        self.create_node("validate", validate_context)
        self.create_node("wait_approval", wait_for_approval)
        self.create_node("save", save_result)

        # Add edges
        self.workflow.add_edge("load", "evaluate")

        self.workflow.add_conditional_edges(
            "evaluate",
            route_after_evaluation,
            {"save": "save", "wait_context": "wait_context"}
        )

        self.workflow.add_edge("wait_context", "validate")

        self.workflow.add_conditional_edges(
            "validate",
            route_after_validation,
            {"wait_approval": "wait_approval", "save": "save"}
        )

        self.workflow.add_edge("wait_approval", "save")
        self.workflow.add_edge("save", END)

        # Compile
        self.app = self.compile()

    def _calculate_score(self, violations):
        """Calculate compliance score"""
        if not violations:
            return 100.0

        severity_weights = {"LOW": 5, "MEDIUM": 15, "HIGH": 25, "CRITICAL": 40}
        deduction = sum(severity_weights.get(v.get("severity", "MEDIUM"), 15) for v in violations)
        return max(0, 100 - deduction)


# Usage example
if __name__ == "__main__":
    workflow = PolicyEvaluationWorkflow()

    # Step 1: Initial evaluation
    result1 = workflow.invoke({
        "document_id": "doc_123",
        "org_id": "org_456"
    }, thread_id="eval_123")

    print("After evaluation:", result1)

    # Step 2: User adds context (resumes workflow)
    result2 = workflow.invoke({
        "custom_context": "VP Sales approved this exception"
    }, thread_id="eval_123")

    print("After context:", result2)
