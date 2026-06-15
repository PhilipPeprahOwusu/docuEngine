# COMPLETE PRD
## Contract Intelligence Agent Platform
### Enterprise-Grade Policy-Governed Contract Management

**Version:** 2.0 - COMPLETE  
**Date:** June 2026  
**Status:** Ready for Development  
**Deployment Target:** AWS  
**Scope:** 50+ hours, 6-7 days  

---

## TABLE OF CONTENTS

1. Executive Summary
2. Vision & Goals
3. User Personas
4. Feature Overview (All Tiers)
5. Architecture & Data Model
6. Agent Factory System
7. Policy Management System
8. Citation & Reference System
9. Notification System
10. User Stories & Workflows
11. API Specifications
12. Database Schema
13. AWS Deployment Plan
14. Timeline & Milestones
15. Success Metrics

---

## 1. EXECUTIVE SUMMARY

**Contract Intelligence Agent Platform** is an enterprise-grade system that uses AI agents to autonomously analyze legal contracts against company policies. Users can create custom agents, upload policies, evaluate contracts with full citations, add context with validation, and receive multi-channel notifications for supervisor approval.

**Key Differentiators:**
- ✅ **Custom Agent Factory** - Users create and configure agents dynamically
- ✅ **Policy-Based Evaluation** - Contracts evaluated against company policies
- ✅ **Full Citation System** - Every violation cites specific policy + contract sections
- ✅ **Custom Context with Validation** - Users add context that's validated against policies
- ✅ **Multi-Channel Notifications** - Slack, Email, Discord approvals
- ✅ **Side-by-Side Comparison** - Visual contract comparison interface

**This demonstrates:**
- Document Intelligence (Evisort) - Contract analysis, extraction, risk assessment
- Agent Orchestration (Sameer) - Custom agents, dynamic creation, tool calling
- Enterprise Governance (Workday) - Multi-tenancy, RBAC, audit logging, compliance

---

## 2. VISION & GOALS

### Vision
Empower organizations to govern contracts through policy-based AI agents that supervisors can configure, customize, and control—with full traceability and multi-channel approval workflows.

### Goals
1. ✅ Build a **custom agent factory** - users create agents for their needs
2. ✅ Implement **policy-based evaluation** - contracts assessed against company rules
3. ✅ Enable **full citation system** - every violation references source policy + contract
4. ✅ Support **custom context validation** - users add insights without violating policies
5. ✅ Deliver **multi-channel notifications** - supervisors approve via Slack/Email/Discord
6. ✅ Deploy **on AWS** with enterprise security and scalability

### Success Metrics
- ✅ Platform deployed and live on AWS
- ✅ All agents function autonomously
- ✅ Custom agents creatable by users
- ✅ Policy evaluations include full citations
- ✅ Custom context validated against policies
- ✅ Notifications work across all channels
- ✅ Complete audit trail maintained
- ✅ Can be demoed in 5-10 minutes
- ✅ Impressed interviewers at Evisort + Workday + Sameer's team

---

## 3. USER PERSONAS

### Persona 1: Legal Analyst
**Goal:** Quickly analyze contracts and understand risks  
**Pain:** Spends hours reading contracts, misses violations, needs consistency  
**Needs:**  
- Upload contracts
- Ask questions about terms
- See policy violations with citations
- Add custom context for exceptions
- Get notifications about approvals

### Persona 2: Procurement Manager
**Goal:** Compare contracts and track obligations  
**Pain:** Hard to compare vendors, track differences, inconsistent terms  
**Needs:**  
- Search and filter contracts
- Side-by-side comparison of contracts
- Compare against company policies
- Track obligations and due dates
- Create custom agents for vendor evaluation

### Persona 3: Compliance Officer
**Goal:** Ensure compliance and maintain audit trail  
**Pain:** No visibility into who accessed what, hard to prove compliance  
**Needs:**  
- View full audit logs
- Track policy exceptions
- Export compliance reports
- See who approved what and when
- Policy version tracking

### Persona 4: Supervisor/Manager
**Goal:** Approve exceptions quickly  
**Pain:** Bottleneck in approvals, hard to review quickly  
**Needs:**  
- Receive notifications (Slack, Email, Discord)
- Review exception details in notification
- Approve/reject without leaving Slack
- See full policy + contract citations
- Track approval history

### Persona 5: Policy Administrator
**Goal:** Manage company policies  
**Pain:** Policies scattered, hard to update, hard to track versions  
**Needs:**  
- Upload and manage policies
- Version control for policies
- See which contracts violate which policies
- Update policies and track impact
- Create policy templates

### Persona 6: Agent Developer (Advanced User)
**Goal:** Create custom agents for specific needs  
**Pain:** Generic agents don't fit specific requirements  
**Needs:**  
- Create new agents with custom prompts
- Configure tools available to agents
- Set parameters (temperature, tokens, etc.)
- Test agents before deployment
- Save and reuse agent configurations

---

## 4. FEATURE OVERVIEW - ALL TIERS

### TIER 1: FOUNDATION (8 hours)
- Multi-tenant database architecture
- RBAC enforcement (Admin, Reviewer, Viewer, Approver)
- Audit logging system (immutable)
- Agent orchestration framework
- Contract ingestion (PDF/DOC upload)
- Basic ASR (Agent System of Record) APIs

### TIER 2: CORE AGENTS (10 hours)
- Extract Agent - information extraction from contracts
- Risk Assessment Agent - identify risks and red flags
- Comparison Agent - compare 2+ contracts side-by-side
- Negotiation Agent - suggest negotiation strategy
- Q&A Agent - answer questions about contracts
- Tool calling and routing logic

### TIER 3: POLICY SYSTEM (12 hours)
- Policy upload and storage
- Policy rule extraction
- Policy-based contract evaluation
- Full citation system (policy + contract references)
- Policy version tracking
- Violation scoring and severity

### TIER 4: CUSTOM CONTEXT & VALIDATION (8 hours)
- User adds custom context/insights
- Contradiction detection (context vs policies)
- Approval workflow for exceptions
- Exception tracking and history
- Context-aware agent decisions
- Supervisor override management

### TIER 5: NOTIFICATIONS (8 hours)
- Multi-channel delivery (Slack, Email, Discord)
- User notification preferences
- Interactive approvals (buttons in Slack/Discord)
- Notification history and audit
- Retry logic for failed notifications
- Rich notification formatting

### TIER 6: AGENT FACTORY (6 hours)
- Create custom agents UI
- Agent configuration interface
- System prompt customization
- Tool selection for agents
- Parameter configuration
- Agent template library
- Test agents before deployment

### TIER 7: ENTERPRISE (4 hours)
- Compliance dashboard
- Admin panel (user management, policies)
- Advanced search and filtering
- Analytics and metrics
- External integrations (DocuSign, Salesforce, Jira)
- Documentation and deployment

---

## 5. ARCHITECTURE & DATA MODEL

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  - Upload, Search, Q&A, Compare                             │
│  - Agent Builder, Policy Manager                            │
│  - Notification Settings, Admin Panel                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            AWS API Gateway + CloudFront                     │
│  - Authentication, Rate Limiting, CORS                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (ECS/Lambda)                   │
│  - Request routing, RBAC enforcement, auth                  │
└──┬──────────┬───────────┬──────────┬──────────┬────────┬────┘
   │          │           │          │          │        │
   ▼          ▼           ▼          ▼          ▼        ▼
┌──────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌──────┐ ┌────────┐
│Extract│ │Risk    │ │Compare   │ │Negotiate│ │Q&A   │ │Custom  │
│Agent  │ │Agent   │ │Agent     │ │Agent    │ │Agent │ │Agents  │
└───┬──┘ └───┬────┘ └────┬─────┘ └────┬────┘ └──┬───┘ └───┬────┘
    │        │           │            │         │         │
    └────────┼───────────┼────────────┼─────────┼─────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Policy Evaluation Engine │
    │ - Compare contract vs    │
    │   company policies       │
    │ - Generate citations     │
    │ - Detect violations      │
    │ - Score severity         │
    └──────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Context Validation Layer │
    │ - Check custom context   │
    │ - Detect contradictions  │
    │ - Route to approvers     │
    └──────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Notification Engine      │
    │ - Multi-channel delivery │
    │ - Interactive approvals  │
    │ - History tracking       │
    └──────────────────────────┘
             │
    ┌────────┴────────┬─────────────┐
    │                 │             │
    ▼                 ▼             ▼
┌────────────┐ ┌──────────┐ ┌─────────────┐
│AWS RDS     │ │ Qdrant   │ │ AWS S3      │
│PostgreSQL  │ │ (Vector) │ │ (Documents) │
└────────────┘ └──────────┘ └─────────────┘

┌────────────────────────────────────────────┐
│ AWS Services                               │
│ - CloudWatch (Monitoring)                  │
│ - Secrets Manager (API Keys)               │
│ - IAM (Access Control)                     │
│ - SQS (Notification Queue)                 │
│ - Lambda (Webhooks)                        │
└────────────────────────────────────────────┘
```

### Data Flow

```
1. USER UPLOADS CONTRACT
   Upload → S3 (storage) → Extract text → Create embeddings
   → Store in RDS + Qdrant → Return with metadata

2. USER CREATES CUSTOM AGENT
   Define prompt → Select tools → Set parameters
   → Save to agent_configs → Ready to use

3. USER UPLOADS POLICY
   Upload policy PDF → Extract rules → Store in policies table
   → Index for search → Ready for evaluation

4. USER EVALUATES CONTRACT AGAINST POLICIES
   Contract + Policies → Policy Evaluation Engine
   → Check each rule → Generate citations → Return violations

5. USER ADDS CUSTOM CONTEXT
   Context → Validation Engine
   → Check against policies → Detect contradictions
   → If clear: save | If contradiction: route to supervisor

6. SUPERVISOR RECEIVES NOTIFICATION
   Event → Notification Engine
   → Route to Slack/Email/Discord
   → Supervisor approves/rejects in notification
   → Update exception status → Audit log

7. FULL AUDIT TRAIL
   Every action logged with:
   - User, timestamp, action, contract, policy reference
   - Citations to policy + contract sections
   - Approval chain and status
```

---

## 6. AGENT FACTORY SYSTEM

### 6.1 Agent Configuration Schema

Every agent has:
```json
{
  "agent_id": "uuid",
  "org_id": "uuid",
  "agent_name": "Payment Terms Specialist",
  "agent_description": "Analyzes and compares payment terms",
  "created_by": "user_id",
  "created_at": "timestamp",
  
  "configuration": {
    "system_prompt": "You are an expert in payment terms...",
    "model": "claude-3.5-sonnet",
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "max_tokens": 2000,
    
    "available_tools": [
      "information_extraction",
      "contract_comparison",
      "risk_assessment",
      "policy_violation_check"
    ],
    
    "output_format": "json",
    "output_schema": {
      "findings": [...],
      "citations": [...],
      "recommendations": [...]
    }
  },
  
  "usage_metrics": {
    "total_invocations": 145,
    "avg_response_time_ms": 2300,
    "success_rate": 0.98
  }
}
```

### 6.2 Agent Builder UI

Users can:
1. **Create Agent** - Name, description, purpose
2. **Configure System Prompt** - What should this agent focus on?
3. **Select Tools** - Which operations can it perform?
4. **Set Parameters** - Temperature, tokens, sampling
5. **Configure Output** - What format should results be in?
6. **Test Agent** - Try it on sample contracts
7. **Save & Deploy** - Make available for use

### 6.3 Pre-Built vs Custom Agents

**Pre-Built (provided):**
- Extract Agent (information extraction)
- Risk Assessment Agent
- Comparison Agent
- Negotiation Agent
- Q&A Agent

**Custom (user-created):**
- Vendor Risk Agent (focused on vendor evaluation)
- Payment Terms Specialist
- Regulatory Compliance Agent
- Industry-Specific Risk Agent
- Custom Domain Agents

### 6.4 Agent Execution Engine

```python
async def execute_agent(agent_id: str, contract_id: str, context: dict):
    """
    1. Load agent configuration
    2. Inject contract data
    3. Apply system prompt
    4. Enable configured tools
    5. Set parameters
    6. Run agent
    7. Return results with citations
    """
    agent = load_agent_config(agent_id)
    contract = get_contract(contract_id)
    
    # Build LangChain agent with config
    agent_executor = create_agent_executor(
        system_prompt=agent.system_prompt,
        tools=agent.available_tools,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens
    )
    
    # Run agent
    result = await agent_executor.run(
        contract=contract,
        context=context
    )
    
    # Log execution
    audit_log(
        action="agent_executed",
        agent_id=agent_id,
        contract_id=contract_id,
        duration_ms=result.execution_time
    )
    
    return result
```

---

## 7. POLICY MANAGEMENT SYSTEM

### 7.1 Policy Upload & Storage

Users upload policy documents (PDF/DOC):
```
Upload → Extract text → Parse rules → Store
```

**Policy data structure:**
```sql
CREATE TABLE company_policies (
    policy_id UUID PRIMARY KEY,
    org_id UUID NOT NULL,
    policy_name VARCHAR(255),
    policy_description TEXT,
    policy_document TEXT, -- Full text
    policy_rules JSONB, -- Extracted rules
    effective_date DATE,
    version VARCHAR(50),
    created_at TIMESTAMP,
    uploaded_by UUID,
    status VARCHAR(50) -- active, archived
);
```

### 7.2 Policy Rules Extraction

System extracts rules from policy document:
```json
{
  "policy_id": "pol_payment_001",
  "policy_name": "Payment Terms Policy",
  "rules": [
    {
      "rule_id": "rule_1",
      "rule_type": "payment_terms",
      "requirement": "All contracts must specify payment terms of Net 30 days",
      "section": "Section 2.1",
      "page": 3,
      "quote": "All contracts must specify payment terms of Net 30 days. Maximum acceptable is Net 45 days for strategic partnerships.",
      "parameters": {
        "default_days": 30,
        "maximum_days": 45,
        "exceptions": ["strategic_partnerships"]
      }
    },
    {
      "rule_id": "rule_2",
      "rule_type": "payment_penalties",
      "requirement": "Late payment penalties must be at least 1.5% per month",
      "section": "Section 2.3",
      "page": 3,
      "quote": "Late payment penalties must be at least 1.5% per month or 18% annually to incentivize timely payment.",
      "parameters": {
        "minimum_monthly_rate": 0.015,
        "minimum_annual_rate": 0.18
      }
    }
  ]
}
```

### 7.3 Policy Version Tracking

```sql
CREATE TABLE policy_versions (
    version_id UUID PRIMARY KEY,
    policy_id UUID NOT NULL,
    version VARCHAR(50),
    effective_date DATE,
    deprecated_date DATE,
    changes_summary TEXT,
    created_at TIMESTAMP
);
```

---

## 8. CITATION & REFERENCE SYSTEM

### 8.1 Full Citation Structure

Every violation includes complete citations:

```json
{
  "violation_id": "vio_12345",
  "contract_id": "con_xyz",
  "severity": "HIGH",
  
  "policy_citation": {
    "policy_id": "pol_payment_001",
    "policy_name": "Payment Terms Policy",
    "policy_version": "1.2",
    "policy_uploaded_date": "2024-06-01T00:00:00Z",
    "effective_date": "2024-06-01",
    
    "rule_citation": {
      "rule_id": "rule_1",
      "requirement_type": "payment_terms",
      "exact_text": "All contracts must specify payment terms of Net 30 days. Maximum acceptable is Net 45 days for strategic partnerships.",
      "section": "Section 2.1",
      "page": 3,
      "paragraph": 2
    },
    
    "enforcement": {
      "mandatory": true,
      "exceptions": ["strategic_partnerships"],
      "approval_required": false
    }
  },
  
  "contract_citation": {
    "contract_id": "con_xyz",
    "contract_name": "XYZ Corp Agreement",
    "exact_text": "Payment shall be due within 60 days of invoice date",
    "section": "Section 3.2",
    "page": 2,
    "paragraph": 1
  },
  
  "violation_analysis": {
    "policy_requirement": "Net 30 (max Net 45)",
    "actual_value": "Net 60",
    "difference": "+15 days",
    "magnitude": "Exceeds maximum by 15 days",
    "impact": "Extends cash flow by 15 days beyond policy limit"
  },
  
  "audit_trail": {
    "detected_at": "2024-06-14T10:30:00Z",
    "detected_by": "policy_evaluation_agent_v1",
    "policy_version_at_detection": "1.2",
    "contract_version_at_detection": "1.0"
  },
  
  "references": {
    "policy_document_url": "/api/policies/pol_payment_001/download",
    "policy_view_url": "/app/policies/pol_payment_001",
    "contract_document_url": "/api/contracts/con_xyz/download",
    "contract_view_url": "/app/contracts/con_xyz",
    "policy_history_url": "/app/policies/pol_payment_001/versions",
    "violation_details_url": "/app/violations/vio_12345"
  }
}
```

### 8.2 Citation Database Schema

```sql
CREATE TABLE policy_violations_with_citations (
    violation_id UUID PRIMARY KEY,
    contract_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    org_id UUID NOT NULL,
    
    -- Policy Citation
    policy_name VARCHAR(255),
    policy_version VARCHAR(50),
    policy_uploaded_date TIMESTAMP,
    policy_effective_date DATE,
    policy_rule_id UUID,
    policy_requirement TEXT,
    policy_section VARCHAR(100),
    policy_page INTEGER,
    policy_quote TEXT, -- Exact quote from policy
    
    -- Contract Citation
    contract_name VARCHAR(255),
    violation_text TEXT, -- Exact text from contract
    violation_section VARCHAR(100),
    violation_page INTEGER,
    violation_paragraph INTEGER,
    
    -- Analysis
    severity VARCHAR(20),
    violation_type VARCHAR(100),
    policy_value VARCHAR(255),
    actual_value VARCHAR(255),
    difference VARCHAR(255),
    impact_description TEXT,
    
    -- Audit
    detected_at TIMESTAMP DEFAULT NOW(),
    detected_by_agent VARCHAR(100),
    policy_version_at_detection VARCHAR(50),
    contract_version_at_detection VARCHAR(50),
    
    -- References
    policy_document_url TEXT,
    contract_document_url TEXT
);

-- Critical indexes for citations
CREATE INDEX idx_violations_policy_id ON policy_violations_with_citations(policy_id);
CREATE INDEX idx_violations_contract_id ON policy_violations_with_citations(contract_id);
CREATE INDEX idx_violations_severity ON policy_violations_with_citations(severity);
```

### 8.3 UI Display with Citations

**Side-by-side view:**
```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│         POLICY REQUIREMENT          │         CONTRACT VIOLATION          │
├─────────────────────────────────────┼─────────────────────────────────────┤
│                                     │                                     │
│ Payment Terms Policy v1.2           │ XYZ Corp Agreement                  │
│ Section 2.1, Page 3                 │ Section 3.2, Page 2                │
│                                     │                                     │
│ "All contracts must specify         │ "Payment shall be due within 60    │
│  payment terms of Net 30 days.      │  days of invoice date"             │
│  Maximum acceptable is Net 45       │                                     │
│  days for strategic partnerships."  │                                     │
│                                     │                                     │
│ Requirement: Net 30 (max Net 45)    │ Contract specifies: Net 60          │
│                                     │                                     │
├─────────────────────────────────────┴─────────────────────────────────────┤
│                                                                             │
│ VIOLATION: Exceeds maximum by 15 days                                      │
│ SEVERITY: HIGH                                                              │
│ IMPACT: Extends cash flow by 15 days beyond policy limit                   │
│                                                                             │
│ [Download Policy] [Download Contract] [View Policy History] [View Details] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. NOTIFICATION SYSTEM

### 9.1 Multi-Channel Notifications

Supervisors get notified through:
- **Slack:** Rich blocks with approval buttons
- **Email:** HTML templates with action links
- **Discord:** Embeds with reaction-based approval

### 9.2 Notification Triggers

```
Trigger 1: Policy violation detected in contract
Trigger 2: Custom context contradicts policy
Trigger 3: Approval required for exception
Trigger 4: Contract status changes
Trigger 5: Policy exception expires soon
```

### 9.3 User Notification Preferences

```sql
CREATE TABLE user_notification_preferences (
    preference_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    org_id UUID NOT NULL,
    
    -- Channel configurations
    slack_enabled BOOLEAN DEFAULT TRUE,
    slack_workspace_token TEXT ENCRYPTED,
    slack_channel_id TEXT,
    slack_user_id TEXT,
    
    email_enabled BOOLEAN DEFAULT TRUE,
    email_address VARCHAR(255),
    
    discord_enabled BOOLEAN DEFAULT FALSE,
    discord_server_id TEXT ENCRYPTED,
    discord_channel_id TEXT,
    discord_user_id TEXT,
    
    -- Notification types
    notify_on_violations BOOLEAN DEFAULT TRUE,
    notify_on_contradictions BOOLEAN DEFAULT TRUE,
    notify_on_approvals BOOLEAN DEFAULT TRUE,
    notify_on_policy_changes BOOLEAN DEFAULT FALSE,
    
    -- Frequency
    batching_enabled BOOLEAN DEFAULT FALSE,
    batch_interval VARCHAR(50), -- "immediate", "hourly", "daily"
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 9.4 Slack Interactive Approval

**Message format:**
```python
slack_message = {
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚨 Policy Exception Approval"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Contract*\nXYZ Corp Agreement"},
                {"type": "mrkdwn", "text": "*Issue*\nPayment Terms (Net 60 vs Net 45)"},
                {"type": "mrkdwn", "text": "*Requested By*\nJohn (Legal)"},
                {"type": "mrkdwn", "text": "*Severity*\nHIGH"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Policy Requirement:*\n\"All contracts must specify payment terms of Net 30 days. Maximum acceptable is Net 45 days.\"\n\n*Contract States:*\n\"Payment shall be due within 60 days of invoice date\"\n\n*Reason:*\nVP Sales approved Net 60 for strategic partnership"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Approve"},
                    "value": "approve_exc_12345",
                    "action_id": "approve_exception",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "❌ Reject"},
                    "value": "reject_exc_12345",
                    "action_id": "reject_exception",
                    "style": "danger"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👀 Full Details"},
                    "value": "review_exc_12345",
                    "action_id": "review_exception"
                }
            ]
        }
    ]
}
```

### 9.5 Email Template

```html
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      
      <h2 style="color: #d32f2f;">🚨 Policy Exception Approval Needed</h2>
      
      <p>Hi <strong>{supervisor_name}</strong>,</p>
      
      <p>A contract exception needs your approval.</p>
      
      <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
        <h3 style="margin-top: 0;">Contract: {contract_name}</h3>
        
        <table style="width: 100%; margin: 10px 0;">
          <tr>
            <td style="font-weight: bold; width: 30%;">Issue:</td>
            <td>{violation_type}</td>
          </tr>
          <tr>
            <td style="font-weight: bold;">Severity:</td>
            <td>{severity}</td>
          </tr>
          <tr>
            <td style="font-weight: bold;">Requested By:</td>
            <td>{requester_name}</td>
          </tr>
        </table>
      </div>
      
      <div style="background: #fff9c4; padding: 15px; border-left: 4px solid #fbc02d; margin: 20px 0;">
        <h3 style="margin-top: 0;">Policy Citation</h3>
        <p><strong>Policy:</strong> {policy_name} v{policy_version}</p>
        <p><strong>Section:</strong> {policy_section}, Page {policy_page}</p>
        <p><em>"{policy_quote}"</em></p>
      </div>
      
      <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
        <h3 style="margin-top: 0;">Contract Violation</h3>
        <p><strong>Section:</strong> {contract_section}, Page {contract_page}</p>
        <p><em>"{violation_text}"</em></p>
      </div>
      
      <div style="margin: 20px 0;">
        <p><strong>Analysis:</strong> {impact_description}</p>
        <p><strong>Reason for Exception:</strong> {custom_context}</p>
      </div>
      
      <div style="text-align: center; margin: 30px 0;">
        <a href="{app_url}/exceptions/{exception_id}/approve" 
           style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 0 10px;">
          ✅ Approve Exception
        </a>
        <a href="{app_url}/exceptions/{exception_id}/reject"
           style="background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 0 10px;">
          ❌ Reject
        </a>
        <a href="{app_url}/contracts/{contract_id}"
           style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 0 10px;">
          👀 View Full Details
        </a>
      </div>
      
      <hr style="margin: 30px 0;">
      
      <p style="font-size: 12px; color: #999;">
        Expires: {expiry_date} | Request ID: {exception_id}
      </p>
      
    </div>
  </body>
</html>
```

### 9.6 Notification History Audit

```sql
CREATE TABLE notification_audit (
    notification_id UUID PRIMARY KEY,
    org_id UUID NOT NULL,
    supervisor_id UUID NOT NULL,
    event_type VARCHAR(100),
    channel VARCHAR(50),
    status VARCHAR(50), -- sent, delivered, clicked, approved, rejected
    contract_id UUID,
    exception_id UUID,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    interacted_at TIMESTAMP,
    interaction_action VARCHAR(100),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);
```

---

## 10. USER STORIES & WORKFLOWS

### Story 1: Upload and Evaluate Contract Against Policies

```
As a Legal Analyst
I want to upload a contract and see how it aligns with company policies
So that I can identify violations and exceptions upfront

Acceptance Criteria:
- Upload PDF/DOC file (< 50MB)
- System extracts contract metadata
- System evaluates against ALL company policies
- For each violation, show:
  - Policy citation (name, version, section, quote)
  - Contract citation (section, quote)
  - Severity level
  - Impact analysis
  - Recommendations
- Results display with side-by-side view of policy vs contract
```

### Story 2: Create Custom Agent

```
As a Procurement Manager
I want to create a custom agent for vendor evaluation
So that I can evaluate all vendor contracts consistently

Acceptance Criteria:
- Click "Create Agent"
- Enter agent name and description
- Write custom system prompt
- Select tools (extraction, comparison, risk, policy check)
- Configure parameters (temperature, max tokens)
- Test on sample contracts
- Save agent configuration
- Agent available in dropdown for future contracts
```

### Story 3: Add Custom Context with Validation

```
As a Legal Analyst
I want to add custom context about a contract exception
But I need to make sure my context doesn't violate company policies

Acceptance Criteria:
- Click "Add Custom Context"
- Enter custom insight (e.g., "VP Sales approved Net 60")
- System validates against policies
- If no contradiction: Save immediately
- If contradiction detected:
  - Flag the contradiction
  - Show which policy it violates
  - Route to supervisor for approval
- If approved: Save with exception flag and audit trail
- If rejected: Ask user to revise
```

### Story 4: Receive and Act on Notifications

```
As a Supervisor
I want to receive notifications about policy exceptions
And approve/reject them directly from Slack/Email
So that I can manage approvals without leaving my communication tool

Acceptance Criteria:
- Receive notification in Slack/Email/Discord
- Notification shows:
  - Contract name
  - Policy violation with citations
  - Custom context from user
  - Approval buttons
- Click "Approve" → Exception approved immediately
- Click "Reject" → Returns to user with comment
- All approvals logged in audit trail
```

### Story 5: Side-by-Side Contract Comparison

```
As a Procurement Manager
I want to compare two contracts side-by-side
So that I can identify differences in terms

Acceptance Criteria:
- Select "Compare Contracts"
- Choose contract A and contract B
- Display side-by-side:
  - Extract terms from both
  - Highlight differences
  - Show which contract is more favorable
- Agent suggests negotiation points based on comparison
- Citations show where each term appears
```

---

## 11. API SPECIFICATIONS

### 11.1 Agent Management APIs

```
POST /api/agents
  Body: {
    name: "Payment Terms Specialist",
    description: "Analyzes payment terms",
    system_prompt: "You are...",
    available_tools: ["extract", "compare", "risk"],
    model: "claude-3.5-sonnet",
    temperature: 0.7
  }
  Response: { agent_id, agent_name, status: "created" }

GET /api/agents
  Response: { agents: [...] }

POST /api/agents/{agent_id}/execute
  Body: { contract_id, context: {} }
  Response: { result, citations, execution_time_ms }
```

### 11.2 Policy Management APIs

```
POST /api/policies
  Body: { file: PDF, policy_name, description }
  Response: { policy_id, status: "uploaded", rules_extracted: 145 }

GET /api/policies/{policy_id}
  Response: { policy, rules: [...], versions: [...] }

GET /api/policies/{policy_id}/violations
  Query: { contract_id?, severity? }
  Response: { violations: [...with full citations...] }
```

### 11.3 Evaluation APIs

```
POST /api/contracts/{contract_id}/evaluate
  Query: { against_policies?, custom_agent_id? }
  Response: {
    violations: [{
      violation_id,
      policy_citation: { policy, rule, section, quote },
      contract_citation: { section, quote },
      severity,
      impact
    }],
    compliance_score: 0-100
  }

POST /api/contracts/{contract_id}/compare
  Body: { other_contract_id }
  Response: {
    differences: [...],
    new_in_b: [...],
    missing_in_b: [...]
  }
```

### 11.4 Context & Exception APIs

```
POST /api/contracts/{contract_id}/context
  Body: { context_text, violation_id? }
  Response: {
    status: "pending_validation" | "saved" | "requires_approval",
    contradictions?: [...]
  }

POST /api/exceptions/{exception_id}/approve
  Body: { approved_by, reason? }
  Response: { success: true, exception_id }

GET /api/exceptions
  Query: { status?, org_id, limit }
  Response: { exceptions: [...], total }
```

### 11.5 Notification APIs

```
POST /api/notifications/preferences
  Body: {
    slack_enabled: true,
    slack_channel_id: "...",
    email_enabled: true,
    email_address: "...",
    discord_enabled: false
  }
  Response: { preference_id, updated }

GET /api/notifications/history
  Query: { status?, date_from, date_to }
  Response: { notifications: [...], total }

POST /api/webhooks/slack/action
  Body: { action_id, value, user_id }
  Response: { success: true, action_taken }
```

---

## 12. DATABASE SCHEMA

### Core Tables

```sql
-- Organizations (Multi-tenancy)
CREATE TABLE organizations (
    org_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    plan VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users (with roles)
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50), -- admin, reviewer, viewer, approver
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_org_id ON users(org_id);

-- Contracts
CREATE TABLE contracts (
    contract_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    filename VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER,
    content TEXT NOT NULL,
    s3_key VARCHAR(500),
    parties TEXT[],
    contract_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(user_id),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_contracts_org_id ON contracts(org_id);

-- Company Policies
CREATE TABLE company_policies (
    policy_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    policy_name VARCHAR(255),
    policy_document TEXT,
    policy_rules JSONB,
    version VARCHAR(50),
    effective_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id),
    status VARCHAR(50) -- active, archived
);
CREATE INDEX idx_policies_org_id ON company_policies(org_id);

-- Policy Violations with Full Citations
CREATE TABLE policy_violations_with_citations (
    violation_id UUID PRIMARY KEY,
    contract_id UUID NOT NULL REFERENCES contracts(contract_id),
    policy_id UUID NOT NULL REFERENCES company_policies(policy_id),
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    
    -- Policy Citation
    policy_name VARCHAR(255),
    policy_version VARCHAR(50),
    policy_section VARCHAR(100),
    policy_page INTEGER,
    policy_quote TEXT,
    
    -- Contract Citation
    contract_name VARCHAR(255),
    violation_text TEXT,
    violation_section VARCHAR(100),
    violation_page INTEGER,
    
    -- Analysis
    severity VARCHAR(20),
    violation_type VARCHAR(100),
    impact_description TEXT,
    
    -- Audit
    detected_at TIMESTAMP DEFAULT NOW(),
    detected_by_agent VARCHAR(100),
    policy_version_at_detection VARCHAR(50)
);
CREATE INDEX idx_violations_policy ON policy_violations_with_citations(policy_id);
CREATE INDEX idx_violations_contract ON policy_violations_with_citations(contract_id);
CREATE INDEX idx_violations_severity ON policy_violations_with_citations(severity);

-- Custom Context
CREATE TABLE custom_context (
    context_id UUID PRIMARY KEY,
    contract_id UUID NOT NULL REFERENCES contracts(contract_id),
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    user_id UUID NOT NULL REFERENCES users(user_id),
    context_text TEXT,
    status VARCHAR(50), -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT NOW(),
    approved_by UUID REFERENCES users(user_id),
    approval_reason TEXT,
    exception_valid_until DATE
);
CREATE INDEX idx_context_contract ON custom_context(contract_id);

-- Policy Exceptions
CREATE TABLE policy_exceptions (
    exception_id UUID PRIMARY KEY,
    contract_id UUID NOT NULL REFERENCES contracts(contract_id),
    policy_id UUID NOT NULL REFERENCES company_policies(policy_id),
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    violation_id UUID REFERENCES policy_violations_with_citations(violation_id),
    
    exception_reason TEXT,
    approved_by UUID NOT NULL REFERENCES users(user_id),
    approval_timestamp TIMESTAMP,
    valid_until DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_exceptions_contract ON policy_exceptions(contract_id);
CREATE INDEX idx_exceptions_policy ON policy_exceptions(policy_id);

-- Custom Agents
CREATE TABLE custom_agents (
    agent_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    agent_name VARCHAR(255),
    agent_description TEXT,
    system_prompt TEXT,
    available_tools TEXT[],
    model VARCHAR(100),
    temperature FLOAT,
    max_tokens INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(user_id),
    status VARCHAR(50) -- active, archived
);
Create INDEX idx_agents_org ON custom_agents(org_id);

-- Immutable Audit Log
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    user_id UUID NOT NULL REFERENCES users(user_id),
    action VARCHAR(100),
    contract_id UUID REFERENCES contracts(contract_id),
    policy_id UUID REFERENCES company_policies(policy_id),
    exception_id UUID REFERENCES policy_exceptions(exception_id),
    agent_id UUID REFERENCES custom_agents(agent_id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    duration_ms INTEGER,
    result_summary VARCHAR(500),
    details JSONB
);
-- Prevent modifications to audit log
CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs DO INSTEAD NOTHING;
CREATE INDEX idx_audit_org ON audit_logs(org_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);

-- User Notification Preferences
CREATE TABLE user_notification_preferences (
    preference_id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id),
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    
    slack_enabled BOOLEAN DEFAULT TRUE,
    slack_workspace_token TEXT ENCRYPTED,
    slack_channel_id TEXT,
    
    email_enabled BOOLEAN DEFAULT TRUE,
    email_address VARCHAR(255),
    
    discord_enabled BOOLEAN DEFAULT FALSE,
    discord_server_id TEXT ENCRYPTED,
    discord_channel_id TEXT,
    
    notify_on_violations BOOLEAN DEFAULT TRUE,
    notify_on_contradictions BOOLEAN DEFAULT TRUE,
    notify_on_approvals BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Audit
CREATE TABLE notification_audit (
    notification_id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(org_id),
    supervisor_id UUID NOT NULL REFERENCES users(user_id),
    event_type VARCHAR(100),
    channel VARCHAR(50), -- slack, email, discord
    status VARCHAR(50), -- sent, delivered, approved, rejected
    contract_id UUID REFERENCES contracts(contract_id),
    exception_id UUID REFERENCES policy_exceptions(exception_id),
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    interacted_at TIMESTAMP,
    interaction_action VARCHAR(100),
    error_message TEXT
);
CREATE INDEX idx_notifications_supervisor ON notification_audit(supervisor_id);
CREATE INDEX idx_notifications_status ON notification_audit(status);
```

---

## 13. AWS DEPLOYMENT PLAN

### Phase 1: Infrastructure (Day 1)

```bash
# RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier contract-intelligence-db \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --engine-version 15 \
  --allocated-storage 100 \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted

# S3 Bucket
aws s3 mb s3://contract-intelligence-docs \
  --region us-east-1
aws s3api put-bucket-versioning \
  --bucket contract-intelligence-docs \
  --versioning-configuration Status=Enabled

# Secrets Manager
aws secretsmanager create-secret \
  --name contract-intelligence/db-password
aws secretsmanager create-secret \
  --name contract-intelligence/anthropic-api-key
```

### Phase 2: Backend Deployment (Day 2-3)

```bash
# Build & Push Docker image to ECR
docker build -t contract-intelligence:latest .
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag contract-intelligence:latest \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/contract-intelligence:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/contract-intelligence:latest

# ECS Cluster
aws ecs create-cluster --cluster-name contract-intelligence

# API Gateway
aws apigateway create-rest-api \
  --name contract-intelligence-api
```

### Phase 3: Frontend Deployment (Day 3)

```bash
# Build React app
cd frontend && npm run build

# Deploy to S3 + CloudFront
aws s3 sync dist/ s3://contract-intelligence-frontend/ --delete
aws cloudfront create-distribution \
  --origin-domain-name contract-intelligence-frontend.s3.amazonaws.com
```

### Terraform IaC (Full Infrastructure)

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier          = "contract-intelligence-db"
  engine              = "postgres"
  engine_version      = "15.3"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 100
  backup_retention_period = 7
  multi_az           = true
  storage_encrypted   = true
}

# S3 Bucket
resource "aws_s3_bucket" "contracts" {
  bucket = "contract-intelligence-docs"
}

resource "aws_s3_bucket_versioning" "contracts" {
  bucket = aws_s3_bucket.contracts.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family = "contract-intelligence"
  container_definitions = jsonencode([{
    name      = "contract-intelligence"
    image     = "${aws_ecr_repository.app.repository_url}:latest"
    cpu       = 512
    memory    = 1024
    port_mappings = [{
      container_port = 8000
      host_port      = 8000
    }]
  }])
}

# ... more resources for ALB, CloudWatch, etc.
```

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t contract-intelligence:${{ github.sha }} .
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | \
            docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/contract-intelligence:latest
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster contract-intelligence \
            --service contract-intelligence \
            --force-new-deployment
      
      - name: Deploy Frontend
        run: |
          cd frontend && npm run build
          aws s3 sync dist/ s3://contract-intelligence-frontend/ --delete
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CF_DIST_ID }} \
            --paths "/*"
```

---

## 14. TIMELINE & MILESTONES

### Day 1 (8 hours): Architecture & Foundation
- [ ] Database schema finalized and created (RDS)
- [ ] RBAC layer implemented
- [ ] Audit logging system built
- [ ] ASR API layer coded
- [ ] AWS infrastructure provisioned
- **Deliverable:** Core infrastructure running

### Day 2 (8 hours): Agents & Evaluation
- [ ] Agent orchestration framework built
- [ ] All 4 pre-built agents implemented
- [ ] Policy evaluation engine implemented
- [ ] Citation system fully integrated
- [ ] Tool calling and routing working
- **Deliverable:** Agents functional with citations

### Day 3 (8 hours): Custom Context & Notifications
- [ ] Custom context layer implemented
- [ ] Contradiction validation working
- [ ] Slack integration complete
- [ ] Email integration complete
- [ ] Discord integration complete
- [ ] Interactive approval workflow tested
- **Deliverable:** Notifications working across channels

### Day 4 (8 hours): Agent Factory & Comparison
- [ ] Agent builder UI coded
- [ ] Agent configuration storage
- [ ] Side-by-side comparison interface
- [ ] Custom agent execution
- [ ] Agent test harness
- **Deliverable:** Users can create and test agents

### Day 5 (6 hours): Enterprise Features
- [ ] Compliance dashboard
- [ ] Admin panel
- [ ] Advanced search/filtering
- [ ] Analytics
- [ ] External integrations (DocuSign, Salesforce)
- **Deliverable:** Full feature set complete

### Days 6-7: Polish & Documentation
- [ ] Testing and bug fixes
- [ ] Performance optimization
- [ ] README and documentation
- [ ] Demo video/walkthrough
- [ ] Deployment verification
- **Deliverable:** Production-ready system live on AWS

---

## 15. SUCCESS METRICS

### Technical Metrics
- ✅ All agents function autonomously
- ✅ Custom agents creatable and deployable
- ✅ Every violation cites policy + contract with exact quotes
- ✅ Custom context validated in < 2 seconds
- ✅ Notifications delivered within 10 seconds
- ✅ Contract evaluation completes in < 15 seconds
- ✅ API availability > 99.9%
- ✅ Complete audit trail maintained

### Portfolio Metrics
- ✅ Code on GitHub with clean structure
- ✅ Deployed and live on AWS
- ✅ Can demo in 5-10 minutes
- ✅ Professional documentation
- ✅ Explains intersection of Evisort + Sameer + Workday

### Interview Metrics
- ✅ Can articulate "at the intersection" positioning
- ✅ Can explain agent factory concept
- ✅ Can discuss policy governance
- ✅ Can show citation system in detail
- ✅ Can demo live system on AWS
- ✅ Can answer deep technical questions
- ✅ Hiring managers impressed

---

## APPENDIX A: TECH STACK

### Backend
- FastAPI 0.104+
- LangChain 0.1+
- Anthropic API (Claude 3.5 Sonnet)
- PostgreSQL 15+
- Qdrant (vector DB)
- Redis (caching)
- boto3 (AWS SDK)

### Frontend
- React 18+
- TypeScript
- TailwindCSS
- React Query
- Axios

### AWS Services
- RDS PostgreSQL
- S3
- API Gateway
- ECS/Fargate or Lambda
- CloudWatch
- Secrets Manager
- IAM
- CloudFront
- SQS (notification queue)

### Integrations
- Slack API
- SMTP (Email)
- Discord API
- DocuSign API
- Salesforce API
- Jira API

---

## APPENDIX B: ENVIRONMENT VARIABLES

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/contract_intelligence
REDIS_URL=redis://cache:6379

# LLM
ANTHROPIC_API_KEY=sk-...

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
S3_BUCKET=contract-intelligence-docs

# Integrations
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

GMAIL_USERNAME=...
GMAIL_APP_PASSWORD=...

DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...

DOCUSIGN_CLIENT_ID=...
DOCUSIGN_CLIENT_SECRET=...

SALESFORCE_API_KEY=...
JIRA_API_KEY=...

# Security
JWT_SECRET_KEY=...
ALGORITHM=HS256
```

---

## APPENDIX C: DOCKER CONFIGURATION

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## END OF COMPLETE PRD

**Version:** 2.0 - COMPREHENSIVE  
**Status:** Ready for Development  
**Last Updated:** June 2026  

This PRD includes:
- ✅ Agent Factory System
- ✅ Policy Management & Evaluation
- ✅ Full Citation System (policy + contract references)
- ✅ Custom Context with Validation
- ✅ Multi-Channel Notifications (Slack, Email, Discord)
- ✅ Side-by-Side Comparison Interface
- ✅ Complete Architecture & Data Model
- ✅ All APIs, Database Schema, Deployment Plan
- ✅ 50+ hour timeline
- ✅ Enterprise-grade security and compliance

