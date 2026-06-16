"""Base Agent Graph for LangGraph workflows"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.agent_state import AgentState
import time
import uuid
from typing import Callable, Dict, Any


class BaseAgentGraph:
    """Base class for all agent graphs"""

    def __init__(self, agent_name: str, llm=None):
        self.agent_name = agent_name
        self.llm = llm
        self.workflow = StateGraph(AgentState)
        self.checkpointer = MemorySaver()
        self.app = None

    def create_node(self, name: str, func: Callable) -> Callable:
        """Create a workflow node with error handling"""
        def node_wrapper(state: AgentState) -> Dict[str, Any]:
            state["step_count"] = state.get("step_count", 0) + 1
            try:
                result = func(state)
                return result
            except Exception as e:
                return {
                    "error": str(e),
                    "execution_duration_ms": int(
                        (time.time() - state.get("execution_start_time", time.time())) * 1000
                    )
                }

        self.workflow.add_node(name, node_wrapper)
        return node_wrapper

    def add_conditional_edge(
        self,
        source: str,
        routing_func: Callable,
        edges: Dict[str, str]
    ):
        """Add conditional edge based on state"""
        def router(state: AgentState) -> str:
            condition = routing_func(state)
            return condition

        self.workflow.add_conditional_edges(source, router, edges)

    def compile(self):
        """Compile workflow into executable graph"""
        return self.workflow.compile(checkpointer=self.checkpointer)

    def invoke(self, input_state: Dict[str, Any], thread_id: str = None) -> Dict[str, Any]:
        """Execute the workflow"""
        initial_state = {
            **input_state,
            "agent_name": self.agent_name,
            "execution_start_time": time.time(),
            "step_count": 0,
            "policy_violations": input_state.get("policy_violations", []),
            "contradictions": input_state.get("contradictions", []),
            "approval_required": input_state.get("approval_required", False),
        }

        config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

        if not self.app:
            raise RuntimeError("Agent not compiled. Call compile() first.")

        result = self.app.invoke(initial_state, config=config)

        # Calculate execution time
        result["execution_duration_ms"] = int(
            (time.time() - result.get("execution_start_time", time.time())) * 1000
        )

        return result

    async def ainvoke(self, input_state: Dict[str, Any], thread_id: str = None) -> Dict[str, Any]:
        """Async execute the workflow"""
        initial_state = {
            **input_state,
            "agent_name": self.agent_name,
            "execution_start_time": time.time(),
            "step_count": 0,
            "policy_violations": input_state.get("policy_violations", []),
            "contradictions": input_state.get("contradictions", []),
            "approval_required": input_state.get("approval_required", False),
        }

        config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

        if not self.app:
            raise RuntimeError("Agent not compiled. Call compile() first.")

        result = await self.app.ainvoke(initial_state, config=config)

        # Calculate execution time
        result["execution_duration_ms"] = int(
            (time.time() - result.get("execution_start_time", time.time())) * 1000
        )

        return result
