"""Risk Assessment Agent"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import assess_risks
from typing import Dict, Any


class RiskAgent(BaseAgentGraph):
    """Assesses risks in documents"""

    def __init__(self, llm=None, db_session=None):
        super().__init__("risk_agent", llm)
        self.db_session = db_session

        def load_document(state: Dict[str, Any]) -> Dict[str, Any]:
            """Load document from database"""
            from app.models.document import Document

            if self.db_session:
                document = self.db_session.query(Document).filter(
                    Document.document_id == state["document_id"]
                ).first()

                if not document:
                    return {"error": f"Document {state['document_id']} not found"}

                return {
                    "document": {
                        "document_id": str(document.document_id),
                        "content": document.content
                    }
                }
            else:
                # Mock for testing
                return {
                    "document": {
                        "document_id": state["document_id"],
                        "content": "Test document with payment terms Net 60, liability cap $500K..."
                    }
                }

        def assess_document_risks(state: Dict[str, Any]) -> Dict[str, Any]:
            """Run risk assessment"""
            risks = assess_risks(state["document"]["content"], self.llm)
            return {"risks": risks}

        def score_risks(state: Dict[str, Any]) -> Dict[str, Any]:
            """Calculate compliance score based on risks"""
            risks = state.get("risks", {})
            violations = state.get("policy_violations", [])

            # Count high severity items
            high_risk_count = sum(
                1 for r in violations
                if r.get("severity") == "HIGH"
            )

            # Simple scoring: start at 100, deduct 20 per high risk
            compliance_score = max(0, 100 - (high_risk_count * 20))

            return {"compliance_score": compliance_score}

        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_document)
        self.create_node("assess", assess_document_risks)
        self.create_node("score", score_risks)
        self.workflow.add_edge("load", "assess")
        self.workflow.add_edge("assess", "score")
        self.workflow.add_edge("score", END)

        # Compile
        self.app = self.compile()


# Usage example
if __name__ == "__main__":
    risk_agent = RiskAgent()
    result = risk_agent.invoke({"document_id": "test_123"})
    print(result)
