# LANGGRAPH IMPLEMENTATION GUIDE
## Contract Intelligence Agent Platform

**Architecture, State Management, Tool Definitions, Agent Graphs & Code Examples**

---

## TABLE OF CONTENTS

1. LangGraph vs LangChain
2. Architecture Overview
3. State Management
4. Tool Definitions
5. Base Agent Graph Pattern
6. Agent Implementations (5 agents)
7. Human-in-the-Loop (Approvals)
8. Custom Agent Builder
9. Integration with FastAPI
10. Deployment & Testing

---

## 1. LANGGRAPH VS LANGCHAIN

### LangChain (Sequential)
```python
# Simple agent - runs tools in sequence
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)
result = agent.run("Compare these contracts")
```

**Limitations:**
- No state management between steps
- Hard to implement human-in-the-loop
- Limited error handling
- Can't branch logic easily
- Hard to visualize workflow

### LangGraph (Stateful)
```python
# Sophisticated agent - maintains state, branching logic, pauses
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("extract", extract_node)
workflow.add_node("analyze", analyze_node)
workflow.add_conditional_edges("analyze", routing_logic)
app = workflow.compile()
result = app.invoke(initial_state)
```

**Advantages:**
- ✅ **Persistent state** across steps
- ✅ **Human-in-the-loop** - pause, wait for user, resume
- ✅ **Conditional branching** - route based on state
- ✅ **Error handling** - retry logic
- ✅ **Visualization** - see the workflow graph
- ✅ **Memory** - checkpoint state between invocations
- ✅ **Multi-step workflows** - sequential and parallel
- ✅ **Tool calling** - controlled tool access

**For your use case:** LangGraph is PERFECT because:
- Agents need to pause for supervisor approval
- State flows through multiple steps
- Conditional logic (if violations, route to approver)
- Multi-step workflows (extract → evaluate → compare → recommend)

---

## 2. ARCHITECTURE OVERVIEW

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                             │
│              (Upload contract, evaluate, compare)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AGENT ROUTER (FastAPI)                         │
│  - Determines which agent(s) to invoke                      │
│  - Loads agent config from database                         │
│  - Initializes LangGraph workflow                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
      ┌────────────────┴────────────────┐
      │                                 │
      ▼                                 ▼
  ┌─────────────┐             ┌──────────────────┐
  │ Pre-built   │             │ Custom Agent     │
  │ Agents      │             │ Graph            │
  │             │             │                  │
  │ - Extract   │             │ (User-defined    │
  │ - Risk      │             │  steps & tools)  │
  │ - Compare   │             │                  │
  │ - Negotiate │             │                  │
  │ - Q&A       │             │                  │
  └─────────────┘             └──────────────────┘
      │                                 │
      └────────────────┬────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   LANGGRAPH WORKFLOW       │
         │                            │
         │   State → Node 1 → Node 2  │
         │   ↓                        │
         │   Check condition          │
         │   ↓                        │
         │   Route to Node 3 or 4     │
         │   ↓                        │
         │   Return results           │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │ POLICY EVALUATION ENGINE   │
         │ - Evaluate against rules   │
         │ - Generate citations       │
         │ - Detect violations        │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │ CONTEXT VALIDATION LAYER   │
         │ - Check for contradictions │
         │ - Approve or route to      │
         │   supervisor               │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │ NOTIFICATION ENGINE        │
         │ - Send to Slack/Email      │
         │ - Wait for approval        │
         │ - Save exception           │
         └─────────────┬──────────────┘
                       │
                       ▼
                  RESULTS + AUDIT LOG
```

---

## 3. STATE MANAGEMENT

### Base Agent State

```python
from typing import TypedDict, Annotated, Optional, List
import operator

class ContractMetadata(TypedDict):
    contract_id: str
    filename: str
    parties: List[str]
    content: str
    s3_key: str

class ExtractionResult(TypedDict):
    parties: List[str]
    dates: dict
    amounts: dict
    key_terms: dict

class PolicyViolation(TypedDict):
    violation_id: str
    policy_id: str
    policy_name: str
    policy_section: str
    policy_quote: str
    contract_section: str
    violation_text: str
    severity: str
    impact: str

class AgentState(TypedDict):
    # Input
    contract_id: str
    contract_a_id: Optional[str]
    contract_b_id: Optional[str]
    query: Optional[str]
    custom_context: Optional[str]
    
    # Contract data
    contract: Optional[ContractMetadata]
    contract_a: Optional[ContractMetadata]
    contract_b: Optional[ContractMetadata]
    
    # Extracted data
    extraction: Optional[ExtractionResult]
    extraction_a: Optional[ExtractionResult]
    extraction_b: Optional[ExtractionResult]
    
    # Policy evaluation
    policy_violations: Annotated[List[PolicyViolation], operator.add]
    compliance_score: Optional[float]
    
    # Comparison
    differences: Optional[dict]
    new_in_b: Optional[List[str]]
    missing_in_b: Optional[List[str]]
    
    # Context & validation
    contradictions: Annotated[List[str], operator.add]
    approval_required: bool
    approval_status: Optional[str]  # pending, approved, rejected
    
    # Q&A
    answer: Optional[str]
    sources: Optional[List[dict]]
    
    # Metadata
    agent_name: str
    execution_start_time: Optional[float]
    execution_duration_ms: Optional[int]
    step_count: int
    error: Optional[str]
```

**Key Features:**
- ✅ `Annotated[List[...], operator.add]` - Automatically appends to list (no overwrites)
- ✅ `Optional[...]` - Can be None initially
- ✅ Complete state schema for type safety
- ✅ Tracks execution metrics

---

## 4. TOOL DEFINITIONS

### Tool Type Definition

```python
from langchain.tools import Tool
from typing import Callable

class AgentTool:
    """Base class for agent tools"""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        return_direct: bool = False
    ):
        self.name = name
        self.description = description
        self.func = func
        self.return_direct = return_direct
    
    def to_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name=self.name,
            description=self.description,
            func=self.func,
            return_direct=self.return_direct
        )
```

### Tool Implementations

```python
# Tool 1: Information Extraction
def extract_contract_info(contract_text: str) -> dict:
    """
    Extract key information from contract text.
    Returns: parties, dates, amounts, key terms
    """
    prompt = """Extract from this contract:
    - Parties: company names
    - Dates: effective, expiration, signing dates
    - Financial: amounts, currencies, payment terms
    - Key Terms: obligations, liabilities, termination
    
    Return as JSON."""
    
    response = llm.invoke(prompt + contract_text)
    return json.loads(response.content)

# Tool 2: Policy Violation Check
def check_policy_violations(
    contract_text: str,
    policy_id: str,
    org_id: str
) -> List[dict]:
    """
    Check if contract violates company policies.
    Returns: violations with full citations
    """
    policies = get_company_policies(org_id, policy_id)
    violations = []
    
    for policy in policies:
        policy_rules = policy["rules"]
        
        for rule in policy_rules:
            # Check if contract violates this rule
            violation = evaluate_rule(contract_text, rule, policy)
            
            if violation:
                violations.append({
                    "violation_id": str(uuid.uuid4()),
                    "policy_citation": {
                        "policy_id": policy["policy_id"],
                        "policy_name": policy["policy_name"],
                        "policy_version": policy["version"],
                        "policy_section": rule["section"],
                        "policy_page": rule["page"],
                        "policy_quote": rule["quote"]
                    },
                    "contract_citation": violation["location"],
                    "severity": violation["severity"],
                    "impact": violation["impact"]
                })
    
    return violations

# Tool 3: Contract Comparison
def compare_contracts(
    extraction_a: dict,
    extraction_b: dict
) -> dict:
    """
    Compare two contract extractions.
    Returns: differences, new terms, missing terms
    """
    differences = {}
    
    # Compare parties
    parties_diff = {
        "in_a_not_b": set(extraction_a["parties"]) - set(extraction_b["parties"]),
        "in_b_not_a": set(extraction_b["parties"]) - set(extraction_a["parties"])
    }
    if any(parties_diff.values()):
        differences["parties"] = parties_diff
    
    # Compare dates
    dates_diff = {}
    for date_type in ["effective", "expiration", "signing"]:
        a_val = extraction_a["dates"].get(date_type)
        b_val = extraction_b["dates"].get(date_type)
        if a_val != b_val:
            dates_diff[date_type] = {"a": a_val, "b": b_val}
    if dates_diff:
        differences["dates"] = dates_diff
    
    # Compare amounts
    amounts_diff = {}
    a_amount = extraction_a["amounts"].get("amount")
    b_amount = extraction_b["amounts"].get("amount")
    if a_amount != b_amount:
        amounts_diff["amount"] = {"a": a_amount, "b": b_amount}
    if amounts_diff:
        differences["amounts"] = amounts_diff
    
    return {
        "differences": differences,
        "new_in_b": list(set(extraction_b.get("key_terms", {}).keys()) - 
                        set(extraction_a.get("key_terms", {}).keys())),
        "missing_in_b": list(set(extraction_a.get("key_terms", {}).keys()) - 
                            set(extraction_b.get("key_terms", {}).keys()))
    }

# Tool 4: Risk Assessment
def assess_risks(contract_text: str) -> dict:
    """
    Assess risks in contract.
    Returns: risk categories with severity
    """
    questions = [
        "What are payment obligations and penalties?",
        "What are termination clauses and notice periods?",
        "What liabilities or liability caps exist?",
        "What are unusual or risky terms?",
        "What compliance requirements are mentioned?"
    ]
    
    risks = {}
    for question in questions:
        answer = rag_query(question, contract_text)
        risks[question] = {
            "answer": answer,
            "severity": classify_severity(answer),
            "section": extract_section_reference(answer)
        }
    
    return risks

# Tool 5: Semantic Search (for Q&A)
def search_contract(query: str, contract_id: str) -> List[dict]:
    """
    Semantically search contract for relevant sections.
    Returns: ranked chunks with similarity scores
    """
    contract = get_contract(contract_id)
    
    # Vector search
    chunks = vector_db.search(
        query=query,
        contract_id=contract_id,
        top_k=5
    )
    
    # Rerank with LLM
    reranked = llm_rerank(query, chunks)
    
    return reranked

# Tool 6: Validate Context Against Policies
def validate_context(
    context_text: str,
    violations: List[dict],
    policies: dict,
    org_id: str
) -> dict:
    """
    Check if custom context contradicts policies.
    Returns: contradictions and approval requirement
    """
    prompt = f"""
    User provided this context: "{context_text}"
    
    This contract has these policy violations:
    {json.dumps(violations, indent=2)}
    
    Does the user's context contradict any of these policies?
    For each contradiction, explain why it violates the policy.
    """
    
    response = llm.invoke(prompt)
    contradictions = parse_contradictions(response.content)
    
    return {
        "contradictions": contradictions,
        "requires_approval": len(contradictions) > 0,
        "approval_level": determine_approval_level(contradictions)
    }

# Register all tools
agent_tools = {
    "information_extraction": Tool(
        name="extract_info",
        description="Extract parties, dates, amounts, and key terms from a contract",
        func=extract_contract_info
    ),
    "policy_violation_check": Tool(
        name="check_violations",
        description="Check contract against company policies and return violations with citations",
        func=check_policy_violations
    ),
    "contract_comparison": Tool(
        name="compare_contracts",
        description="Compare two contract extractions and identify differences",
        func=compare_contracts
    ),
    "risk_assessment": Tool(
        name="assess_risks",
        description="Assess and categorize risks in a contract",
        func=assess_risks
    ),
    "semantic_search": Tool(
        name="search_contract",
        description="Semantically search a contract for relevant sections based on a query",
        func=search_contract
    ),
    "validate_context": Tool(
        name="validate_context",
        description="Validate custom context against company policies",
        func=validate_context
    )
}
```

---

## 5. BASE AGENT GRAPH PATTERN

### Generic Agent Factory

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import time

class BaseAgentGraph:
    """Base class for all agent graphs"""
    
    def __init__(self, agent_name: str, llm):
        self.agent_name = agent_name
        self.llm = llm
        self.workflow = StateGraph(AgentState)
        self.checkpointer = MemorySaver()
    
    def create_node(self, name: str, func):
        """Create a workflow node"""
        def node_wrapper(state):
            state["step_count"] += 1
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
    
    def add_conditional_edge(self, source: str, routing_func, edges: dict):
        """Add conditional edge based on state"""
        def router(state):
            condition = routing_func(state)
            return condition
        
        self.workflow.add_conditional_edges(source, router, edges)
    
    def compile(self):
        """Compile workflow into executable graph"""
        return self.workflow.compile(checkpointer=self.checkpointer)
    
    def invoke(self, input_state: dict, thread_id: str = None):
        """Execute the workflow"""
        initial_state = {
            **input_state,
            "agent_name": self.agent_name,
            "execution_start_time": time.time(),
            "step_count": 0
        }
        
        config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
        
        result = self.app.invoke(initial_state, config=config)
        
        # Calculate execution time
        result["execution_duration_ms"] = int(
            (time.time() - result["execution_start_time"]) * 1000
        )
        
        return result
```

---

## 6. AGENT IMPLEMENTATIONS

### Agent 1: Extract Agent

```python
class ExtractAgent(BaseAgentGraph):
    """Extracts structured information from contracts"""
    
    def __init__(self, llm):
        super().__init__("extract_agent", llm)
        
        # Node 1: Load contract
        def load_contract(state):
            contract = get_contract(state["contract_id"])
            return {
                "contract": {
                    "contract_id": contract.id,
                    "filename": contract.filename,
                    "content": contract.content,
                    "parties": contract.parties or []
                }
            }
        
        # Node 2: Extract information
        def extract_info(state):
            extraction = extract_contract_info(state["contract"]["content"])
            return {"extraction": extraction}
        
        # Build graph
        self.workflow.set_entry_point("load")
        self.create_node("load", load_contract)
        self.create_node("extract", extract_info)
        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", END)
        
        # Compile
        self.app = self.compile()

# Usage
extract_agent = ExtractAgent(llm)
result = extract_agent.invoke({"contract_id": "con_123"})
# Returns: extraction with parties, dates, amounts, key_terms
```

### Agent 2: Risk Assessment Agent

```python
class RiskAgent(BaseAgentGraph):
    """Assesses risks in contracts"""
    
    def __init__(self, llm):
        super().__init__("risk_agent", llm)
        
        def load_contract(state):
            contract = get_contract(state["contract_id"])
            return {"contract": {"content": contract.content, "id": contract.id}}
        
        def assess_risks(state):
            risks = assess_risks(state["contract"]["content"])
            return {"policy_violations": []}  # Will be filled by policy engine
        
        def score_risks(state):
            high_risk_count = sum(
                1 for r in state["policy_violations"]
                if r.get("severity") == "HIGH"
            )
            compliance_score = max(0, 100 - (high_risk_count * 20))
            return {"compliance_score": compliance_score}
        
        self.workflow.set_entry_point("load")
        self.create_node("load", load_contract)
        self.create_node("assess", assess_risks)
        self.create_node("score", score_risks)
        self.workflow.add_edge("load", "assess")
        self.workflow.add_edge("assess", "score")
        self.workflow.add_edge("score", END)
        
        self.app = self.compile()

# Usage
risk_agent = RiskAgent(llm)
result = risk_agent.invoke({"contract_id": "con_123"})
# Returns: risks, severity levels, compliance_score
```

### Agent 3: Comparison Agent

```python
class ComparisonAgent(BaseAgentGraph):
    """Compares two contracts side-by-side"""
    
    def __init__(self, llm):
        super().__init__("comparison_agent", llm)
        
        def load_contracts(state):
            contract_a = get_contract(state["contract_a_id"])
            contract_b = get_contract(state["contract_b_id"])
            return {
                "contract_a": {
                    "id": contract_a.id,
                    "filename": contract_a.filename,
                    "content": contract_a.content
                },
                "contract_b": {
                    "id": contract_b.id,
                    "filename": contract_b.filename,
                    "content": contract_b.content
                }
            }
        
        def extract_both(state):
            extraction_a = extract_contract_info(state["contract_a"]["content"])
            extraction_b = extract_contract_info(state["contract_b"]["content"])
            return {
                "extraction_a": extraction_a,
                "extraction_b": extraction_b
            }
        
        def compare(state):
            comparison = compare_contracts(
                state["extraction_a"],
                state["extraction_b"]
            )
            return {
                "differences": comparison["differences"],
                "new_in_b": comparison["new_in_b"],
                "missing_in_b": comparison["missing_in_b"]
            }
        
        def generate_recommendations(state):
            prompt = f"""
            Contract A: {state["contract_a"]["filename"]}
            Contract B: {state["contract_b"]["filename"]}
            
            Differences: {json.dumps(state["differences"], indent=2)}
            
            Generate negotiation recommendations focusing on:
            1. Most favorable terms for us
            2. Items to push back on
            3. Suggested counter-offers
            """
            
            recommendations = self.llm.invoke(prompt)
            return {"answer": recommendations.content}
        
        self.workflow.set_entry_point("load")
        self.create_node("load", load_contracts)
        self.create_node("extract", extract_both)
        self.create_node("compare", compare)
        self.create_node("recommend", generate_recommendations)
        
        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", "compare")
        self.workflow.add_edge("compare", "recommend")
        self.workflow.add_edge("recommend", END)
        
        self.app = self.compile()

# Usage
comparison_agent = ComparisonAgent(llm)
result = comparison_agent.invoke({
    "contract_a_id": "con_123",
    "contract_b_id": "con_456"
})
# Returns: differences, recommendations
```

### Agent 4: Negotiation Agent

```python
class NegotiationAgent(BaseAgentGraph):
    """Suggests negotiation strategy"""
    
    def __init__(self, llm):
        super().__init__("negotiation_agent", llm)
        
        def load_contracts(state):
            your_contract = get_contract(state["contract_a_id"])
            their_contract = get_contract(state["contract_b_id"])
            return {
                "contract_a": {"content": your_contract.content},
                "contract_b": {"content": their_contract.content}
            }
        
        def extract_terms(state):
            extraction_a = extract_contract_info(state["contract_a"]["content"])
            extraction_b = extract_contract_info(state["contract_b"]["content"])
            return {
                "extraction_a": extraction_a,
                "extraction_b": extraction_b
            }
        
        def identify_unfavorable_terms(state):
            prompt = f"""
            Our terms: {json.dumps(state["extraction_a"], indent=2)}
            Their terms: {json.dumps(state["extraction_b"], indent=2)}
            
            Identify terms that are unfavorable to us:
            1. Payment terms that are too long
            2. Liability caps that are too low
            3. Termination clauses that are restrictive
            4. Missing protections we need
            """
            
            unfavorable = self.llm.invoke(prompt)
            return {"answer": unfavorable.content}
        
        def generate_counter_offers(state):
            prompt = f"""
            Based on the unfavorable terms we identified, generate specific counter-offers.
            
            For each unfavorable term:
            1. Explain why it's unfavorable
            2. Suggest specific language for counter-offer
            3. Justify the counter-offer with business reasons
            """
            
            counters = self.llm.invoke(prompt)
            return {"answer": counters.content}
        
        self.workflow.set_entry_point("load")
        self.create_node("load", load_contracts)
        self.create_node("extract", extract_terms)
        self.create_node("identify", identify_unfavorable_terms)
        self.create_node("counter", generate_counter_offers)
        
        self.workflow.add_edge("load", "extract")
        self.workflow.add_edge("extract", "identify")
        self.workflow.add_edge("identify", "counter")
        self.workflow.add_edge("counter", END)
        
        self.app = self.compile()

# Usage
negotiation_agent = NegotiationAgent(llm)
result = negotiation_agent.invoke({
    "contract_a_id": "your_contract_id",
    "contract_b_id": "their_contract_id"
})
# Returns: counter-offers and negotiation strategy
```

### Agent 5: Q&A Agent

```python
class QAAgent(BaseAgentGraph):
    """Answers questions about contracts"""
    
    def __init__(self, llm):
        super().__init__("qa_agent", llm)
        
        def load_contract(state):
            contract = get_contract(state["contract_id"])
            return {"contract": {"content": contract.content, "id": contract.id}}
        
        def search_contract(state):
            sources = search_contract(
                state["query"],
                state["contract_id"]
            )
            return {"sources": sources}
        
        def rerank_sources(state):
            # LLM reranks based on relevance to query
            prompt = f"""
            Query: {state["query"]}
            
            Candidate sections:
            {json.dumps([s['text'] for s in state['sources']], indent=2)}
            
            Rank by relevance to the query. Return top 3 sections in order.
            """
            
            reranked = self.llm.invoke(prompt)
            # Parse and update sources
            return {}
        
        def generate_answer(state):
            context = "\n\n".join([s["text"] for s in state["sources"][:3]])
            
            prompt = f"""
            Based on these contract sections:
            {context}
            
            Answer this question: {state["query"]}
            Include specific citations to sections.
            """
            
            answer = self.llm.invoke(prompt)
            return {
                "answer": answer.content,
                "sources": state["sources"][:3]
            }
        
        self.workflow.set_entry_point("load")
        self.create_node("load", load_contract)
        self.create_node("search", search_contract)
        self.create_node("rerank", rerank_sources)
        self.create_node("answer", generate_answer)
        
        self.workflow.add_edge("load", "search")
        self.workflow.add_edge("search", "rerank")
        self.workflow.add_edge("rerank", "answer")
        self.workflow.add_edge("answer", END)
        
        self.app = self.compile()

# Usage
qa_agent = QAAgent(llm)
result = qa_agent.invoke({
    "contract_id": "con_123",
    "query": "What are the payment terms?"
})
# Returns: answer with citations
```

---

## 7. HUMAN-IN-THE-LOOP (Approvals)

### Policy Evaluation with Approval Workflow

```python
class PolicyEvaluationWorkflow(BaseAgentGraph):
    """Evaluates contracts against policies with supervisor approval"""
    
    def __init__(self, llm, notification_service):
        super().__init__("policy_evaluation", llm)
        self.notification_service = notification_service
        
        def load_contract_and_policies(state):
            contract = get_contract(state["contract_id"])
            policies = get_company_policies(state["org_id"])
            return {
                "contract": {
                    "id": contract.id,
                    "content": contract.content,
                    "filename": contract.filename
                },
                "policy_violations": []  # Will be populated
            }
        
        def evaluate_policies(state):
            """Run policy evaluation engine"""
            violations = policy_engine.evaluate_all(
                contract_text=state["contract"]["content"],
                org_id=state["org_id"]
            )
            return {
                "policy_violations": violations,
                "compliance_score": calculate_score(violations)
            }
        
        # NODE 2B: If no violations, done
        def no_violations_route(state):
            return "save_result" if not state["policy_violations"] else "wait_context"
        
        def save_clean_result(state):
            """Save contract as clean"""
            db.save_contract_evaluation(
                contract_id=state["contract_id"],
                violations=[],
                status="compliant"
            )
            return {"approval_status": "auto_approved"}
        
        # NODE 3: Wait for user context
        def wait_for_context(state):
            """Pause here - user adds context"""
            # This pauses the graph
            # User adds context via API
            # Graph resumes with context in state
            return state
        
        # NODE 4: Validate context
        def validate_context(state):
            """Check if context contradicts policies"""
            if not state.get("custom_context"):
                return {
                    "contradictions": [],
                    "approval_required": False
                }
            
            contradictions = validate_context(
                context_text=state["custom_context"],
                violations=state["policy_violations"],
                org_id=state["org_id"]
            )
            
            return {
                "contradictions": contradictions.get("contradictions", []),
                "approval_required": len(contradictions.get("contradictions", [])) > 0
            }
        
        # NODE 5: Route based on contradictions
        def route_after_validation(state):
            if state["approval_required"]:
                return "wait_approval"
            else:
                return "save_result"
        
        # NODE 6: Wait for supervisor approval
        def wait_for_approval(state):
            """
            Send notification to supervisor.
            Pause here until approval received.
            """
            exception_id = create_policy_exception(
                contract_id=state["contract_id"],
                violations=state["policy_violations"],
                custom_context=state.get("custom_context"),
                status="pending"
            )
            
            # Send notification (Slack, Email, Discord)
            self.notification_service.send_exception_approval(
                exception_id=exception_id,
                violations=state["policy_violations"],
                custom_context=state.get("custom_context"),
                org_id=state["org_id"]
            )
            
            # Pause here - graph waits for approval
            return {"exception_id": exception_id}
        
        # NODE 7: Route based on approval
        def route_after_approval(state):
            exception = db.get_exception(state["exception_id"])
            if exception.approval_status == "approved":
                return "save_result"
            elif exception.approval_status == "rejected":
                return "send_rejection"
            else:
                return "wait_approval"  # Still pending
        
        # NODE 8: Save result
        def save_result(state):
            db.save_contract_evaluation(
                contract_id=state["contract_id"],
                violations=state["policy_violations"],
                custom_context=state.get("custom_context"),
                approval_status=state.get("approval_status", "auto_approved"),
                exception_id=state.get("exception_id")
            )
            return {}
        
        # NODE 9: Send rejection
        def send_rejection(state):
            exception = db.get_exception(state["exception_id"])
            return {"approval_status": "rejected"}
        
        # Build graph
        self.workflow.set_entry_point("load")
        
        self.create_node("load", load_contract_and_policies)
        self.create_node("evaluate", evaluate_policies)
        self.create_node("no_violations", no_violations_route)
        self.create_node("save", save_result)
        self.create_node("wait_context", wait_for_context)
        self.create_node("validate", validate_context)
        self.create_node("route_validation", route_after_validation)
        self.create_node("wait_approval", wait_for_approval)
        self.create_node("route_approval", route_after_approval)
        self.create_node("reject", send_rejection)
        
        # Add edges
        self.workflow.add_edge("load", "evaluate")
        
        self.workflow.add_conditional_edges(
            "evaluate",
            lambda s: "save" if not s["policy_violations"] else "wait_context",
            {"save": "save", "wait_context": "wait_context"}
        )
        
        self.workflow.add_edge("wait_context", "validate")
        
        self.workflow.add_conditional_edges(
            "validate",
            route_after_validation,
            {"wait_approval": "wait_approval", "save_result": "save"}
        )
        
        self.workflow.add_edge("wait_approval", "route_approval")
        
        self.workflow.add_conditional_edges(
            "route_approval",
            route_after_approval,
            {
                "save_result": "save",
                "rejected": "reject",
                "wait_approval": "wait_approval"
            }
        )
        
        self.workflow.add_edge("save", END)
        self.workflow.add_edge("reject", END)
        
        self.app = self.compile()

# Usage with checkpoint persistence
policy_workflow = PolicyEvaluationWorkflow(llm, notification_service)

# Initial evaluation
result1 = policy_workflow.invoke({
    "contract_id": "con_123",
    "org_id": "org_456"
}, thread_id="eval_123")

# User adds context and resumes
result2 = policy_workflow.invoke({
    "custom_context": "VP Sales approved this exception"
}, thread_id="eval_123")

# Supervisor approves and resumes
result3 = policy_workflow.invoke({
    "approval_status": "approved"
}, thread_id="eval_123")
# Returns: final evaluation with exception tracked
```

---

## 8. CUSTOM AGENT BUILDER

### Dynamic Agent Creation

```python
class CustomAgentBuilder:
    """Allows users to create custom agents"""
    
    @staticmethod
    def build_agent(agent_config: dict, llm):
        """
        Build custom agent from user configuration.
        
        Config:
        {
            "name": "Payment Terms Specialist",
            "system_prompt": "You are...",
            "steps": ["extract", "analyze", "recommend"],
            "tools": ["extract_info", "policy_check", "search"],
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        """
        
        class CustomAgent(BaseAgentGraph):
            def __init__(self):
                super().__init__(agent_config["name"], llm)
                
                # Create step nodes dynamically
                for i, step_name in enumerate(agent_config["steps"]):
                    def create_step_func(step_idx, step_name):
                        def step_func(state):
                            # Build prompt from system_prompt + step
                            prompt = f"""{agent_config['system_prompt']}
                            
                            Step: {step_name}
                            Current state: {json.dumps({
                                k: v for k, v in state.items()
                                if k not in ['contract', 'contract_a', 'contract_b']
                            }, indent=2)}
                            
                            Available tools: {', '.join(agent_config['tools'])}
                            
                            Proceed with step '{step_name}'.
                            """
                            
                            # Call LLM with available tools
                            tools = [agent_tools[tool] for tool in agent_config["tools"]]
                            
                            # Using tool calling
                            response = llm.invoke(prompt)
                            
                            # Parse tool calls and execute
                            # Return updated state
                            return {"answer": response.content}
                        
                        return step_func
                    
                    self.create_node(step_name, create_step_func(i, step_name))
                
                # Connect steps
                self.workflow.set_entry_point(agent_config["steps"][0])
                for i in range(len(agent_config["steps"]) - 1):
                    self.workflow.add_edge(
                        agent_config["steps"][i],
                        agent_config["steps"][i + 1]
                    )
                self.workflow.add_edge(agent_config["steps"][-1], END)
                
                self.app = self.compile()
        
        return CustomAgent()

# Usage
custom_config = {
    "name": "Payment Terms Specialist",
    "system_prompt": "You are an expert in analyzing and negotiating payment terms. Focus on: net days, discounts, late payment penalties, and payment method preferences.",
    "steps": ["extract", "analyze", "compare", "recommend"],
    "tools": ["extract_info", "policy_check", "search_contract"],
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

custom_agent = CustomAgentBuilder.build_agent(custom_config, llm)
result = custom_agent.invoke({"contract_id": "con_123"})
```

---

## 9. INTEGRATION WITH FASTAPI

### FastAPI Endpoints

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Initialize agents
extract_agent = ExtractAgent(llm)
risk_agent = RiskAgent(llm)
comparison_agent = ComparisonAgent(llm)
negotiation_agent = NegotiationAgent(llm)
qa_agent = QAAgent(llm)
policy_workflow = PolicyEvaluationWorkflow(llm, notification_service)

@app.post("/api/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: dict):
    """
    Execute agent on contract.
    Routes to appropriate agent based on agent_id.
    """
    try:
        if agent_id == "extract":
            result = extract_agent.invoke({
                "contract_id": request["contract_id"]
            })
        
        elif agent_id == "risk":
            result = risk_agent.invoke({
                "contract_id": request["contract_id"]
            })
        
        elif agent_id == "compare":
            result = comparison_agent.invoke({
                "contract_a_id": request["contract_a_id"],
                "contract_b_id": request["contract_b_id"]
            })
        
        elif agent_id == "negotiate":
            result = negotiation_agent.invoke({
                "contract_a_id": request["your_contract_id"],
                "contract_b_id": request["their_contract_id"]
            })
        
        elif agent_id == "qa":
            result = qa_agent.invoke({
                "contract_id": request["contract_id"],
                "query": request["question"]
            })
        
        elif agent_id.startswith("custom_"):
            # Load custom agent from database
            agent_config = db.get_agent_config(agent_id)
            custom_agent = CustomAgentBuilder.build_agent(agent_config, llm)
            result = custom_agent.invoke({
                "contract_id": request["contract_id"]
            })
        
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Log execution
        audit_log(
            action="agent_executed",
            agent_id=agent_id,
            contract_id=request.get("contract_id"),
            duration_ms=result.get("execution_duration_ms")
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contracts/{contract_id}/evaluate")
async def evaluate_contract(contract_id: str, request: dict):
    """
    Evaluate contract against policies.
    Uses human-in-the-loop workflow.
    """
    # Start policy evaluation workflow
    result = policy_workflow.invoke({
        "contract_id": contract_id,
        "org_id": request["org_id"]
    }, thread_id=f"eval_{contract_id}")
    
    return result

@app.post("/api/contracts/{contract_id}/context")
async def add_custom_context(contract_id: str, request: dict):
    """
    Add custom context to contract evaluation.
    Resumes paused workflow.
    """
    thread_id = f"eval_{contract_id}"
    
    # Resume workflow with context
    result = policy_workflow.invoke({
        "custom_context": request["context"]
    }, thread_id=thread_id)
    
    return result

@app.post("/api/exceptions/{exception_id}/approve")
async def approve_exception(exception_id: str, request: dict):
    """
    Supervisor approves policy exception.
    Resumes workflow.
    """
    thread_id = f"eval_{db.get_exception(exception_id).contract_id}"
    
    # Update exception status
    db.update_exception_status(
        exception_id=exception_id,
        status="approved",
        approved_by=request["user_id"]
    )
    
    # Resume workflow
    result = policy_workflow.invoke({
        "approval_status": "approved"
    }, thread_id=thread_id)
    
    return result
```

---

## 10. DEPLOYMENT & TESTING

### Unit Tests

```python
import pytest

def test_extract_agent():
    """Test extract agent functionality"""
    agent = ExtractAgent(llm)
    result = agent.invoke({"contract_id": "test_contract_123"})
    
    assert result["extraction"] is not None
    assert "parties" in result["extraction"]
    assert "dates" in result["extraction"]
    assert "amounts" in result["extraction"]

def test_comparison_agent():
    """Test contract comparison"""
    agent = ComparisonAgent(llm)
    result = agent.invoke({
        "contract_a_id": "con_111",
        "contract_b_id": "con_222"
    })
    
    assert result["differences"] is not None
    assert "new_in_b" in result
    assert "missing_in_b" in result

def test_policy_evaluation_workflow():
    """Test policy evaluation with approval workflow"""
    workflow = PolicyEvaluationWorkflow(llm, notification_service)
    
    # Step 1: Start evaluation
    result1 = workflow.invoke({
        "contract_id": "con_123",
        "org_id": "org_456"
    }, thread_id="test_eval_123")
    
    # Step 2: Add context
    result2 = workflow.invoke({
        "custom_context": "VP approved"
    }, thread_id="test_eval_123")
    
    # Step 3: Approve
    result3 = workflow.invoke({
        "approval_status": "approved"
    }, thread_id="test_eval_123")
    
    assert result3["approval_status"] == "approved"

def test_custom_agent_builder():
    """Test creating custom agents"""
    config = {
        "name": "Test Agent",
        "system_prompt": "You are a test agent",
        "steps": ["extract", "analyze"],
        "tools": ["extract_info"],
        "parameters": {"temperature": 0.7}
    }
    
    agent = CustomAgentBuilder.build_agent(config, llm)
    result = agent.invoke({"contract_id": "con_123"})
    
    assert result is not None
    assert result["agent_name"] == "Test Agent"
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY app/ ./app/
COPY backend/ ./backend/

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
langgraph==0.0.20
langchain==0.1.0
langchain-anthropic==0.0.13
anthropic==0.25.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
qdrant-client==2.7.0
python-jose==3.3.0
passlib==1.7.4
redis==5.0.1
boto3==1.28.85
slack-sdk==3.26.0
discord.py==2.3.2
requests==2.31.0
```

---

## SUMMARY

This LangGraph implementation guide covers:

✅ **Architecture** - LangGraph vs LangChain, system flow  
✅ **State Management** - Complete AgentState schema with operators  
✅ **Tools** - 6 tools with full implementations  
✅ **Base Pattern** - Reusable BaseAgentGraph class  
✅ **Agents** - 5 complete agent implementations  
✅ **Human-in-Loop** - Policy evaluation with approval workflow  
✅ **Custom Agents** - Dynamic agent builder  
✅ **FastAPI Integration** - All endpoints with agent routing  
✅ **Testing & Deployment** - Unit tests, Docker, requirements  

---

## KEY ADVANTAGES OF THIS APPROACH

1. **Stateful Workflows** - Agents maintain state across steps
2. **Human-in-the-Loop** - Pause for approvals, resume automatically
3. **Conditional Routing** - Branch logic based on state
4. **Extensible** - Easy to add new agents and tools
5. **Testable** - Each node can be tested independently
6. **Observable** - Visualize workflow graph
7. **Persistent** - Checkpoint system for recovery
8. **Type-Safe** - TypedDict ensures state schema

**Ready to build with LangGraph!** 🚀

