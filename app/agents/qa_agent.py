"""Q&A Agent - Answers questions about documents"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import search_document
from typing import Dict, Any


class QAAgent(BaseAgentGraph):
    """Answers questions about documents using semantic search + LLM"""

    def __init__(self, llm=None, db_session=None, vector_db=None):
        super().__init__("qa_agent", llm)
        self.db_session = db_session
        self.vector_db = vector_db

        def load_document(state: Dict[str, Any]) -> Dict[str, Any]:
            """Load document"""
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
                return {
                    "document": {
                        "document_id": state["document_id"],
                        "content": "Mock document with payment terms Net 30..."
                    }
                }

        def search_document_sections(state: Dict[str, Any]) -> Dict[str, Any]:
            """Semantic search for relevant sections"""
            sources = search_document(
                state["query"],
                state["document_id"],
                self.vector_db
            )

            return {"sources": sources}

        def rerank_sources(state: Dict[str, Any]) -> Dict[str, Any]:
            """LLM reranks sources by relevance"""
            if not self.llm:
                # Skip reranking if no LLM
                return {}

            sources = state["sources"]
            if len(sources) <= 3:
                # No need to rerank
                return {}

            # For now, just keep top 3
            # In production, would use LLM to rerank
            return {}

        def generate_answer(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate answer from sources"""
            sources = state["sources"][:3]  # Top 3
            context = "\n\n".join([s["text"] for s in sources])

            if not self.llm:
                return {
                    "answer": f"Mock answer: Based on the document, {context[:100]}...",
                    "sources": sources
                }

            prompt = f"""
            Based on these document sections:
            {context}

            Answer this question: {state["query"]}

            Include specific citations to sections.
            Be precise and quote exact language where relevant.
            """

            answer = self.llm.invoke(prompt)
            return {
                "answer": answer.content,
                "sources": sources
            }

        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_document)
        self.create_node("search", search_document_sections)
        self.create_node("rerank", rerank_sources)
        self.create_node("generate", generate_answer)

        self.workflow.add_edge("load", "search")
        self.workflow.add_edge("search", "rerank")
        self.workflow.add_edge("rerank", "generate")
        self.workflow.add_edge("generate", END)

        # Compile
        self.app = self.compile()


# Usage example
if __name__ == "__main__":
    qa_agent = QAAgent()
    result = qa_agent.invoke({
        "document_id": "doc_123",
        "query": "What are the payment terms?"
    })
    print(result)
