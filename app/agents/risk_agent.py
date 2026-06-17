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

            # Count severity levels from risk assessment
            high_count = 0
            medium_count = 0
            low_count = 0

            for risk_category, risk_data in risks.items():
                if risk_category == "extraction_error":
                    # If there was an extraction error, return a neutral score
                    return {"compliance_score": 50}

                if isinstance(risk_data, dict):
                    severity = risk_data.get("severity", "LOW")
                    if severity == "HIGH":
                        high_count += 1
                    elif severity == "MEDIUM":
                        medium_count += 1
                    elif severity == "LOW":
                        low_count += 1

            # Scoring: Start at 100, deduct points based on severity
            # HIGH risks: -15 points each
            # MEDIUM risks: -8 points each
            # LOW risks: -3 points each
            compliance_score = 100 - (high_count * 15) - (medium_count * 8) - (low_count * 3)
            compliance_score = max(0, min(100, compliance_score))  # Clamp between 0-100

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
