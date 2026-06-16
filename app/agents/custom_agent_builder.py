"""Custom Agent Factory - Allows users to create custom agents"""
from langgraph.graph import END
from app.agents.base_agent import BaseAgentGraph
from app.agents.tools import get_agent_tools
from typing import Dict, Any
import json


class CustomAgentBuilder:
    """Factory for building custom agents from user configurations"""

    @staticmethod
    def build_agent(agent_config: Dict[str, Any], llm=None, db_session=None):
        """
        Build custom agent from configuration.

        Config structure:
        {
            "agent_id": "uuid",
            "agent_name": "Payment Terms Specialist",
            "agent_description": "Analyzes payment terms",
            "system_prompt": "You are an expert in...",
            "available_tools": ["extract_info", "policy_check"],
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        """

        class DynamicCustomAgent(BaseAgentGraph):
            """Dynamically created custom agent"""

            def __init__(self):
                super().__init__(agent_config["agent_name"], llm)
                self.config = agent_config
                self.db = db_session

                # Get tools
                all_tools = get_agent_tools(llm, None, None)
                self.tools = {
                    name: tool
                    for name, tool in all_tools.items()
                    if name in agent_config.get("available_tools", [])
                }

                # Build workflow from config
                self._build_workflow()

            def _build_workflow(self):
                """Build workflow based on configuration"""

                # Node 1: Load document
                def load_document(state: Dict[str, Any]) -> Dict[str, Any]:
                    """Load document"""
                    from app.models.document import Document

                    if not self.db:
                        return {
                            "document": {
                                "document_id": state["document_id"],
                                "content": "Test document..."
                            }
                        }

                    document = self.db.query(Document).filter(
                        Document.document_id == state["document_id"]
                    ).first()

                    if not document:
                        return {"error": "Document not found"}

                    return {
                        "document": {
                            "document_id": str(document.document_id),
                            "content": document.content
                        }
                    }

                # Node 2: Execute custom logic
                def execute_custom_logic(state: Dict[str, Any]) -> Dict[str, Any]:
                    """Run custom agent logic with LLM"""
                    if not self.llm:
                        return {"answer": f"Mock answer from {self.config['agent_name']}"}

                    system_prompt = self.config["system_prompt"]
                    document_content = state["document"]["content"][:3000]

                    prompt = f"""{system_prompt}

                    Available tools: {', '.join(self.tools.keys())}

                    Document:
                    {document_content}

                    Query: {state.get("query", "Analyze this document")}

                    Analyze and provide insights based on your specialization.
                    """

                    # Call LLM with configured parameters
                    response = self.llm.invoke(
                        prompt,
                        temperature=self.config.get("temperature", 0.7),
                        max_tokens=self.config.get("max_tokens", 2000)
                    )

                    return {"answer": response.content}

                # Build simple 2-node workflow
                self.workflow.set_entry_point("load")
                self.create_node("load", load_document)
                self.create_node("execute", execute_custom_logic)
                self.workflow.add_edge("load", "execute")
                self.workflow.add_edge("execute", END)

                # Compile
                self.app = self.compile()

        return DynamicCustomAgent()

    @staticmethod
    def save_agent_config(
        agent_config: Dict[str, Any],
        org_id: str,
        user_id: str,
        db_session
    ):
        """Save custom agent configuration to database"""
        from app.models.custom_agent import CustomAgent
        import uuid

        agent = CustomAgent(
            agent_id=uuid.uuid4(),
            org_id=org_id,
            agent_name=agent_config["agent_name"],
            agent_description=agent_config.get("agent_description"),
            system_prompt=agent_config["system_prompt"],
            available_tools=agent_config.get("available_tools", []),
            model=agent_config.get("model", "claude-3-5-sonnet-20241022"),
            temperature=agent_config.get("temperature", 0.7),
            max_tokens=agent_config.get("max_tokens", 2000),
            created_by=user_id,
            status="active"
        )

        db_session.add(agent)
        db_session.commit()

        return str(agent.agent_id)

    @staticmethod
    def load_agent_config(agent_id: str, db_session):
        """Load agent configuration from database"""
        from app.models.custom_agent import CustomAgent

        agent = db_session.query(CustomAgent).filter(
            CustomAgent.agent_id == agent_id
        ).first()

        if not agent:
            return None

        return {
            "agent_id": str(agent.agent_id),
            "agent_name": agent.agent_name,
            "agent_description": agent.agent_description,
            "system_prompt": agent.system_prompt,
            "available_tools": agent.available_tools,
            "model": agent.model,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens
        }


# Usage example
if __name__ == "__main__":
    # Create custom agent
    custom_config = {
        "agent_name": "Payment Terms Specialist",
        "agent_description": "Analyzes payment terms in detail",
        "system_prompt": "You are an expert in analyzing payment terms. Focus on: net days, discounts, late payment penalties, and payment method preferences.",
        "available_tools": ["extract_info", "policy_check"],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    custom_agent = CustomAgentBuilder.build_agent(custom_config)
    result = custom_agent.invoke({
        "document_id": "doc_123",
        "query": "What are the payment terms?"
    })

    print(result)
