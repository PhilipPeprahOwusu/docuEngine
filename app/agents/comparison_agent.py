"""Comparison Agent - Side-by-side document comparison"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import extract_document_info, compare_documents
from typing import Dict, Any
import json


class ComparisonAgent(BaseAgentGraph):
    """Compares two documents side-by-side"""

    def __init__(self, llm=None, db_session=None):
        super().__init__("comparison_agent", llm)
        self.db_session = db_session

        def load_documents(state: Dict[str, Any]) -> Dict[str, Any]:
            """Load both documents"""
            from app.models.document import Document

            if self.db_session:
                document_a = self.db_session.query(Document).filter(
                    Document.document_id == state["document_a_id"]
                ).first()
                document_b = self.db_session.query(Document).filter(
                    Document.document_id == state["document_b_id"]
                ).first()

                if not document_a or not document_b:
                    return {"error": "One or both documents not found"}

                return {
                    "document_a": {
                        "document_id": str(document_a.document_id),
                        "filename": document_a.filename,
                        "content": document_a.content
                    },
                    "document_b": {
                        "document_id": str(document_b.document_id),
                        "filename": document_b.filename,
                        "content": document_b.content
                    }
                }
            else:
                # Mock
                return {
                    "document_a": {
                        "document_id": state["document_a_id"],
                        "filename": "document_a.pdf",
                        "content": "Document A: Net 30 payment terms..."
                    },
                    "document_b": {
                        "document_id": state["document_b_id"],
                        "filename": "document_b.pdf",
                        "content": "Document B: Net 60 payment terms..."
                    }
                }

        def extract_both(state: Dict[str, Any]) -> Dict[str, Any]:
            """Extract info from both documents"""
            extraction_a = extract_document_info(
                state["document_a"]["content"],
                self.llm
            )
            extraction_b = extract_document_info(
                state["document_b"]["content"],
                self.llm
            )

            return {
                "extraction_a": extraction_a,
                "extraction_b": extraction_b
            }

        def compare(state: Dict[str, Any]) -> Dict[str, Any]:
            """Compare the two extractions"""
            comparison = compare_documents(
                state["extraction_a"],
                state["extraction_b"]
            )

            return {
                "differences": comparison["differences"],
                "new_in_b": comparison["new_in_b"],
                "missing_in_b": comparison["missing_in_b"]
            }

        def generate_recommendations(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate negotiation recommendations"""
            if not self.llm:
                return {
                    "recommendations": "Mock recommendation: Document B has more favorable payment terms."
                }

            prompt = f"""
            Document A: {state["document_a"]["filename"]}
            Document B: {state["document_b"]["filename"]}

            Differences: {json.dumps(state["differences"], indent=2)}
            New terms in B: {state["new_in_b"]}
            Missing in B: {state["missing_in_b"]}

            Generate negotiation recommendations focusing on:
            1. Most favorable terms for us
            2. Items to push back on
            3. Suggested counter-offers
            """

            recommendations = self.llm.invoke(prompt)
            return {"recommendations": recommendations.content}

        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_documents)
        self.create_node("extract", extract_both)
        self.create_node("compare", compare)
        self.create_node("recommend", generate_recommendations)

        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", "compare")
        self.workflow.add_edge("compare", "recommend")
        self.workflow.add_edge("recommend", END)

        # Compile
        self.app = self.compile()


# Usage example
if __name__ == "__main__":
    comparison_agent = ComparisonAgent()
    result = comparison_agent.invoke({
        "document_a_id": "doc_123",
        "document_b_id": "doc_456"
    })
    print(result)
