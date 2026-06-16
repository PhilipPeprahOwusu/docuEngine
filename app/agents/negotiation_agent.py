"""Negotiation Agent - Suggests negotiation strategy"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import extract_document_info
from typing import Dict, Any
import json


class NegotiationAgent(BaseAgentGraph):
    """Suggests negotiation strategy based on document comparison"""

    def __init__(self, llm=None, db_session=None):
        super().__init__("negotiation_agent", llm)
        self.db_session = db_session

        def load_documents(state: Dict[str, Any]) -> Dict[str, Any]:
            """Load our document and their document"""
            from app.models.document import Document

            if self.db_session:
                your_document = self.db_session.query(Document).filter(
                    Document.document_id == state["document_a_id"]
                ).first()
                their_document = self.db_session.query(Document).filter(
                    Document.document_id == state["document_b_id"]
                ).first()

                if not your_document or not their_document:
                    return {"error": "One or both documents not found"}

                return {
                    "document_a": {"content": your_document.content},
                    "document_b": {"content": their_document.content}
                }
            else:
                return {
                    "document_a": {"content": "Our standard document with Net 30 terms..."},
                    "document_b": {"content": "Their proposed document with Net 60 terms..."}
                }

        def extract_terms(state: Dict[str, Any]) -> Dict[str, Any]:
            """Extract terms from both documents"""
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

        def identify_unfavorable_terms(state: Dict[str, Any]) -> Dict[str, Any]:
            """Identify terms that are unfavorable to us"""
            if not self.llm:
                return {
                    "answer": "Mock: Their Net 60 payment terms are unfavorable (15 days longer than our standard)"
                }

            prompt = f"""
            Our standard terms: {json.dumps(state["extraction_a"], indent=2)}
            Their proposed terms: {json.dumps(state["extraction_b"], indent=2)}

            Identify terms that are unfavorable to us:
            1. Payment terms that are too long
            2. Liability caps that are too low
            3. Termination clauses that are restrictive
            4. Missing protections we need
            """

            unfavorable = self.llm.invoke(prompt)
            return {"answer": unfavorable.content}

        def generate_counter_offers(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate specific counter-offers"""
            if not self.llm:
                return {
                    "counter_offers": [
                        {
                            "issue": "Payment Terms",
                            "their_position": "Net 60",
                            "our_counter": "Net 45",
                            "justification": "Industry standard for strategic partnerships"
                        }
                    ]
                }

            prompt = f"""
            Based on the unfavorable terms identified:
            {state["answer"]}

            Generate specific counter-offers for each unfavorable term.

            For each:
            1. Explain why it's unfavorable
            2. Suggest specific language for counter-offer
            3. Justify the counter-offer with business reasons

            Return as JSON list of counter-offers.
            """

            counters = self.llm.invoke(prompt)
            try:
                return {"counter_offers": json.loads(counters.content)}
            except:
                return {"counter_offers": []}

        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_documents)
        self.create_node("extract", extract_terms)
        self.create_node("identify", identify_unfavorable_terms)
        self.create_node("counter", generate_counter_offers)

        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", "identify")
        self.workflow.add_edge("identify", "counter")
        self.workflow.add_edge("counter", END)

        # Compile
        self.app = self.compile()


# Usage example
if __name__ == "__main__":
    negotiation_agent = NegotiationAgent()
    result = negotiation_agent.invoke({
        "document_a_id": "our_document",
        "document_b_id": "their_document"
    })
    print(result)
