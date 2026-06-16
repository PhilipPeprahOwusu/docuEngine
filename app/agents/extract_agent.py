"""Extract Agent - Information Extraction from Documents"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import extract_document_info
from typing import Dict, Any


class ExtractAgent(BaseAgentGraph):
    """Extracts structured information from documents"""

    def __init__(self, llm=None, db_session=None):
        super().__init__("extract_agent", llm)
        self.db_session = db_session

        # Node 1: Load document
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
                        "filename": document.filename,
                        "content": document.content,
                        "parties": document.parties or [],
                        "s3_key": document.s3_key
                    }
                }
            else:
                # Mock for testing
                return {
                    "document": {
                        "document_id": state["document_id"],
                        "filename": "test_document.pdf",
                        "content": "This is a test document between Company A and Company B...",
                        "parties": [],
                        "s3_key": None
                    }
                }

        # Node 2: Extract information
        def extract_info(state: Dict[str, Any]) -> Dict[str, Any]:
            """Extract structured data from document"""
            document_content = state["document"]["content"]
            extraction = extract_document_info(document_content, self.llm)

            return {"extraction": extraction}

        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_document)
        self.create_node("extract", extract_info)
        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", END)

        # Compile
        self.app = self.compile()


# Usage example
if __name__ == "__main__":
    extract_agent = ExtractAgent()
    result = extract_agent.invoke({"document_id": "test_123"})
    print(result)
