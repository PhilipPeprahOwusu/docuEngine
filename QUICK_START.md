# Quick Start Guide - Document Intelligence Platform

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Anthropic API key

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env - REQUIRED fields:
DATABASE_URL=postgresql://user:password@localhost:5432/contract_intelligence
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Setup Database

```bash
# Create database
createdb contract_intelligence

# Run migrations
alembic upgrade head
```

### Step 4: Run Server

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

---

## 🧪 Testing Agents (Python REPL)

### Extract Agent

```python
from app.agents import ExtractAgent
from app.db.session import SessionLocal
from anthropic import Anthropic

# Setup
db = SessionLocal()
llm = Anthropic(api_key="your-key")
agent = ExtractAgent(llm, db)

# Run
result = agent.invoke({"contract_id": "test_123"})
print(result["extraction"])
# Output: {"parties": [...], "dates": {...}, "amounts": {...}}
```

### Risk Agent

```python
from app.agents import RiskAgent

agent = RiskAgent(llm, db)
result = agent.invoke({"contract_id": "test_123"})
print(f"Compliance Score: {result['compliance_score']}")
print(f"Risks: {result['risks']}")
```

### Comparison Agent

```python
from app.agents import ComparisonAgent

agent = ComparisonAgent(llm, db)
result = agent.invoke({
    "contract_a_id": "con_111",
    "contract_b_id": "con_222"
})
print(f"Differences: {result['differences']}")
print(f"Recommendations: {result['recommendations']}")
```

### Q&A Agent

```python
from app.agents import QAAgent

agent = QAAgent(llm, db)
result = agent.invoke({
    "contract_id": "con_123",
    "query": "What are the payment terms?"
})
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

---

## 🔄 Policy Evaluation Workflow

### Full Workflow with Human-in-the-Loop

```python
from app.agents.policy_evaluation_workflow import PolicyEvaluationWorkflow
from app.services.policy_engine import PolicyEvaluationEngine
from app.services.notification_service import NotificationService

# Setup
policy_engine = PolicyEvaluationEngine(db, llm)
notification_service = NotificationService(db)
workflow = PolicyEvaluationWorkflow(llm, db, policy_engine, notification_service)

# Step 1: Initial evaluation
result1 = workflow.invoke({
    "contract_id": "con_123",
    "org_id": "org_456"
}, thread_id="eval_123")

print(f"Violations found: {len(result1['policy_violations'])}")
print(f"Compliance score: {result1['compliance_score']}")

# Step 2: User adds context
result2 = workflow.invoke({
    "custom_context": "VP Sales approved Net 60 for strategic partnership"
}, thread_id="eval_123")  # Same thread_id resumes workflow

# Step 3: If contradiction detected, supervisor gets notification
# Supervisor approves via Slack/Email/Discord
# Workflow completes automatically
```

---

## 🏭 Custom Agent Factory

### Create a Custom Agent

```python
from app.agents.custom_agent_builder import CustomAgentBuilder

# Define agent configuration
config = {
    "agent_name": "Payment Terms Specialist",
    "agent_description": "Expert in analyzing payment terms",
    "system_prompt": """You are an expert in payment terms.
    Focus on: net days, discounts, penalties, payment methods.
    Identify favorable and unfavorable terms.""",
    "available_tools": ["extract_info", "policy_check"],
    "temperature": 0.7,
    "max_tokens": 2000
}

# Build agent
custom_agent = CustomAgentBuilder.build_agent(config, llm, db)

# Use agent
result = custom_agent.invoke({
    "contract_id": "con_123",
    "query": "Analyze payment terms"
})

print(result["answer"])

# Save configuration to database
agent_id = CustomAgentBuilder.save_agent_config(
    config,
    org_id="org_456",
    user_id="user_123",
    db_session=db
)

print(f"Agent saved with ID: {agent_id}")
```

---

## 📧 Notification Service

### Send Approval Notification

```python
from app.services.notification_service import NotificationService

notification_service = NotificationService(db)

# Send multi-channel notification
notification_service.send_exception_approval(
    exception_id="exc_123",
    violations=[{
        "policy_name": "Payment Terms Policy",
        "policy_quote": "Net 30 maximum",
        "violation_text": "Net 60 specified",
        "severity": "HIGH",
        "contract_name": "XYZ Corp Agreement"
    }],
    custom_context="VP approved for strategic partnership",
    org_id="org_456"
)

# Sends to all supervisors via:
# - Slack (interactive blocks)
# - Email (HTML template)
# - Discord (rich embed)
```

---

## 🗄️ Database Models Quick Reference

### Create Organization

```python
from app.models import Organization

org = Organization(
    name="Acme Corp",
    plan="enterprise"
)
db.add(org)
db.commit()
```

### Create User

```python
from app.models import User
from app.core.security import get_password_hash

user = User(
    org_id=org.org_id,
    email="john@acme.com",
    name="John Doe",
    password_hash=get_password_hash("password123"),
    role="admin",  # admin, reviewer, viewer, approver
    is_active=True
)
db.add(user)
db.commit()
```

### Create Contract

```python
from app.models import Contract

contract = Contract(
    org_id=org.org_id,
    filename="vendor_agreement.pdf",
    content="Full contract text here...",
    s3_key="contracts/vendor_agreement.pdf",
    parties=["Acme Corp", "Vendor Inc"],
    contract_type="vendor_agreement",
    created_by=user.user_id
)
db.add(contract)
db.commit()
```

### Create Policy

```python
from app.models import CompanyPolicy

policy = CompanyPolicy(
    org_id=org.org_id,
    policy_name="Payment Terms Policy",
    policy_document="Full policy text...",
    policy_rules={
        "rules": [
            {
                "rule_id": "rule_1",
                "rule_type": "payment_terms",
                "requirement": "Net 30 days maximum",
                "section": "Section 2.1",
                "page": 3,
                "quote": "All contracts must specify payment terms of Net 30 days.",
                "parameters": {
                    "default_days": 30,
                    "maximum_days": 45
                }
            }
        ]
    },
    version="1.0",
    status="active",
    created_by=user.user_id
)
db.add(policy)
db.commit()
```

---

## 🔧 API Examples (Future)

### Upload Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contract.pdf" \
  -F "org_id=org_456"
```

### Execute Agent

```bash
curl -X POST http://localhost:8000/api/v1/agents/extract/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "con_123"}'
```

### Evaluate Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts/con_123/evaluate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"org_id": "org_456"}'
```

### Add Context

```bash
curl -X POST http://localhost:8000/api/v1/contracts/con_123/context \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"context": "VP Sales approved"}'
```

### Approve Exception

```bash
curl -X POST http://localhost:8000/api/v1/exceptions/exc_123/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "reason": "Strategic partnership"}'
```

---

## 📊 Monitoring & Debugging

### View Audit Logs

```python
from app.models import AuditLog

logs = db.query(AuditLog).filter(
    AuditLog.org_id == "org_456"
).order_by(AuditLog.timestamp.desc()).limit(10).all()

for log in logs:
    print(f"{log.timestamp}: {log.action} by {log.user_id}")
```

### Check Violations

```python
from app.models import PolicyViolation

violations = db.query(PolicyViolation).filter(
    PolicyViolation.contract_id == "con_123"
).all()

for v in violations:
    print(f"Policy: {v.policy_name}")
    print(f"Severity: {v.severity}")
    print(f"Impact: {v.impact_description}")
```

### View Notifications

```python
from app.models import NotificationAudit

notifications = db.query(NotificationAudit).filter(
    NotificationAudit.supervisor_id == "user_123"
).all()

for n in notifications:
    print(f"{n.channel}: {n.status} at {n.sent_at}")
```

---

## 🐛 Troubleshooting

### Issue: Database connection error
**Solution:** Check DATABASE_URL in .env, ensure PostgreSQL is running

### Issue: LLM API error
**Solution:** Verify ANTHROPIC_API_KEY is correct

### Issue: Agent returns mock data
**Solution:** Ensure LLM is properly initialized and passed to agent

### Issue: Workflow doesn't pause
**Solution:** Use same thread_id when resuming workflow

---

## 💡 Tips & Best Practices

1. **Always use thread_id** for workflows that need to pause/resume
2. **Mock first, integrate later** for faster development
3. **Check audit logs** for debugging
4. **Use RBAC** for multi-user scenarios
5. **Test with small contracts** first

---

## 📚 Additional Resources

- Full PRD: `docs/COMPLETE_PRD_Contract_Intelligence_Agent_Platform.md`
- LangGraph Guide: `docs/LANGGRAPH_Implementation_Guide.md`
- Implementation Log: `IMPLEMENTATION_LOG.md`
- Project Summary: `PROJECT_SUMMARY.md`

---

**Questions?** Check the detailed documentation or implementation log for design decisions and trade-offs.
