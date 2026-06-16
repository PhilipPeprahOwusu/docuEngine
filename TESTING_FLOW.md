# DocuEngine Testing Flow & Use Cases

## Overview
This document outlines test cases for all key features and AI agents in the DocuEngine platform. Each feature/agent includes 2 use cases with step-by-step flows for manual testing.

---

## 1. Document Upload Feature

### Use Case 1.1: Upload Single Contract PDF
**Goal**: Verify successful upload and processing of a PDF contract

**Test Flow**:
1. Navigate to Dashboard > Documents
2. Click "Upload Document" button
3. Select a contract PDF file (e.g., "SaaS_Agreement.pdf")
4. Choose document type: "Contract"
5. Click "Upload"
6. **Expected Result**:
   - Upload progress indicator appears
   - Success notification displayed
   - Document appears in documents list with correct filename
   - Document status shows "Processed"

### Use Case 1.2: Upload Multiple Documents (Batch)
**Goal**: Test bulk upload functionality

**Test Flow**:
1. Navigate to Dashboard > Documents
2. Click "Upload Document" button
3. Select multiple files (3-5 different contracts)
4. Verify all files appear in upload queue
5. Click "Upload All"
6. **Expected Result**:
   - All documents upload successfully
   - Each document appears in list with unique ID
   - Total document count increases correctly
   - No duplicate entries

---

## 2. Extract Agent

### Use Case 2.1: Extract Key Information from Employment Contract
**Goal**: Verify extraction of parties, dates, and key terms

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Extract Information" card
3. From dropdown, select an employment contract
4. Click "Run Extract Agent"
5. Wait for analysis to complete
6. **Expected Result**:
   - Loading spinner shows during processing
   - Results display structured data cards including:
     - Party names (Employee, Employer)
     - Contract dates (Start date, End date)
     - Salary/compensation details
     - Key clauses (termination, confidentiality)
   - Data is formatted cleanly (not raw JSON)

### Use Case 2.2: Extract Information from Multi-Party Agreement
**Goal**: Test extraction on complex document with 3+ parties

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Extract Information" card
3. Select a joint venture or partnership agreement
4. Click "Run Extract Agent"
5. Review extracted information
6. **Expected Result**:
   - All parties correctly identified
   - Entity relationships mapped
   - Payment terms and obligations extracted
   - Key dates and milestones captured
   - No data mixing between different parties

---

## 3. Risk Agent

### Use Case 3.1: Assess Liability Risks in Vendor Contract
**Goal**: Identify liability caps, indemnification issues

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Risk Assessment" card
3. Choose a vendor/supplier contract
4. Click "Run Risk Agent"
5. Wait for analysis completion
6. **Expected Result**:
   - Compliance score displayed (0-100%)
   - Risk categories shown with severity levels
   - Specific risks identified:
     - Unlimited liability clauses
     - Missing indemnification
     - Unfavorable payment terms
   - Each risk has description and impact assessment

### Use Case 3.2: Compliance Check for NDA Agreement
**Goal**: Verify compliance with standard NDA policies

**Test Flow**:
1. Upload a non-disclosure agreement
2. Navigate to Dashboard > AI Analysis
3. Select "Risk Assessment" card
4. Choose the uploaded NDA
5. Click "Run Risk Agent"
6. **Expected Result**:
   - Compliance score > 70% for standard NDA
   - Risk assessment includes:
     - Confidentiality scope review
     - Duration/term analysis
     - Return of information clauses
     - Non-solicitation terms (if any)
   - Green badge if compliant, red if issues found

---

## 4. Comparison Agent

### Use Case 4.1: Compare Contract Versions (v1 vs v2)
**Goal**: Identify changes between contract revisions

**Test Flow**:
1. Upload two versions of the same contract (e.g., MSA v1.0 and v1.1)
2. Navigate to Dashboard > AI Analysis
3. Select "Compare Documents" card
4. Select first document (v1.0) in first dropdown
5. Select second document (v1.1) in second dropdown
6. Click "Run Compare Agent"
7. **Expected Result**:
   - Comparison results grouped by sections
   - Changes highlighted (additions, deletions, modifications)
   - Key differences called out:
     - Payment term changes
     - Liability cap modifications
     - New/removed clauses
   - Side-by-side or diff view format

### Use Case 4.2: Compare Contracts from Different Vendors
**Goal**: Benchmark terms across multiple vendor agreements

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Compare Documents" card
3. Select Vendor A contract in first dropdown
4. Select Vendor B contract in second dropdown
5. Click "Run Compare Agent"
6. **Expected Result**:
   - Structured comparison showing:
     - Pricing differences
     - SLA commitments comparison
     - Warranty terms side-by-side
     - Liability and indemnification comparison
   - Clear visualization of favorable vs unfavorable terms
   - Recommendation or score for each vendor

---

## 5. Q&A Agent

### Use Case 5.1: Ask Specific Question About Payment Terms
**Goal**: Test natural language question answering

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Ask Questions" card
3. Choose a contract with payment terms
4. Enter question: "What is the payment schedule and when are invoices due?"
5. Click "Ask Question"
6. **Expected Result**:
   - Loading indicator during processing
   - Answer appears in clean card format
   - Response includes:
     - Specific payment schedule (e.g., "Net 30 days")
     - Invoice timing details
     - Quote from relevant contract section
   - Answer is conversational and accurate

### Use Case 5.2: Multi-Part Question About Termination
**Goal**: Test complex reasoning across multiple clauses

**Test Flow**:
1. Navigate to Dashboard > AI Analysis
2. Select "Ask Questions" card
3. Choose a service agreement
4. Enter question: "Who can terminate the contract, under what conditions, and what is the notice period?"
5. Click "Ask Question"
6. **Expected Result**:
   - Comprehensive answer covering all parts:
     - Parties with termination rights
     - Conditions for termination (for cause, convenience)
     - Notice period requirements (e.g., 30 days written notice)
   - Citations to specific contract sections
   - Structured format (bullet points if multiple conditions)

---

## 6. Custom Agent Creation Feature

### Use Case 6.1: Create SaaS Contract Specialist Agent
**Goal**: Build custom agent for SaaS-specific analysis

**Test Flow**:
1. Navigate to Dashboard > AI Agents
2. Click "Create Custom Agent" button
3. Fill in form:
   - Name: "SaaS Contract Reviewer"
   - Description: "Specialized agent for SaaS agreements"
   - System Prompt: "You are an expert in SaaS contracts. Analyze data privacy, SLA commitments, uptime guarantees, and subscription terms."
   - Temperature: 0.3
   - Max Tokens: 4000
4. Click "Create Agent"
5. **Expected Result**:
   - Success message displayed
   - New agent appears in Custom Agents section
   - Agent card shows all entered details
   - Can view configuration settings
   - Ready to run on documents

### Use Case 6.2: Create Real Estate Lease Analyzer
**Goal**: Build agent for lease agreement analysis

**Test Flow**:
1. Navigate to Dashboard > AI Agents
2. Click "Create Custom Agent"
3. Fill in form:
   - Name: "Commercial Lease Analyzer"
   - Description: "Reviews commercial real estate leases"
   - System Prompt: "Expert in commercial leases. Extract rent escalation clauses, CAM charges, lease terms, renewal options, and tenant improvements."
   - Temperature: 0.2
   - Max Tokens: 5000
4. Click "Create Agent"
5. **Expected Result**:
   - Agent created successfully
   - Appears in custom agents list
   - Can edit configuration
   - Can execute on uploaded lease documents
   - Returns lease-specific insights

---

## 7. Policy Management Feature

### Use Case 7.1: Create Liability Cap Policy
**Goal**: Define policy requiring max $1M liability cap

**Test Flow**:
1. Navigate to Dashboard > Policies
2. Click "Create Policy" button
3. Enter policy details:
   - Name: "Maximum Liability Cap"
   - Description: "All contracts must limit liability to $1M or company annual revenue"
   - Policy rules: Define liability threshold
   - Status: Active
4. Click "Save Policy"
5. **Expected Result**:
   - Policy created and appears in list
   - Status badge shows "Active"
   - Version number assigned (v1.0)
   - Total policy count increases
   - Policy can be edited or deactivated

### Use Case 7.2: Upload Policy Document (Compliance Manual)
**Goal**: Import existing policy document

**Test Flow**:
1. Navigate to Dashboard > Policies
2. Click "Upload Policy Doc" button
3. Select PDF compliance manual
4. Review parsed policy content
5. Confirm upload
6. **Expected Result**:
   - Document uploaded successfully
   - Policy content extracted
   - Appears in policies list
   - Can be referenced by risk agent
   - Version tracking enabled

---

## 8. Slack Notifications Feature

### Use Case 8.1: Configure Risk Alert Webhook
**Goal**: Set up Slack alerts for high-risk contracts

**Test Flow**:
1. Navigate to Dashboard > Integrations > Slack
2. Enter Slack webhook URL for risk alerts channel
3. Click "Test Webhook" button
4. Verify test message appears in Slack
5. Click "Save Configuration"
6. Upload high-risk contract
7. Run Risk Agent on contract
8. **Expected Result**:
   - Test notification appears in Slack channel
   - Configuration saved successfully
   - When risk score < 50%, automatic Slack alert sent
   - Alert includes:
     - Document name
     - Risk score
     - Top 3 risks
     - Link to view details

### Use Case 8.2: Configure Contract Intake Notifications
**Goal**: Get Slack notifications when new contracts uploaded

**Test Flow**:
1. Navigate to Dashboard > Integrations > Slack
2. Enter webhook URL for contract intake channel
3. Enable "Contract Intake" notifications
4. Upload new contract document
5. **Expected Result**:
   - Slack message sent immediately upon upload
   - Message includes:
     - Contract filename
     - Upload timestamp
     - Uploaded by (user)
     - Document type
     - Link to view document

---

## 9. Exception Approval Workflow

### Use Case 9.1: Request Exception for Policy Violation
**Goal**: Request approval for non-standard contract term

**Test Flow**:
1. Run Risk Agent on contract with policy violations
2. Navigate to violation details
3. Click "Request Exception" button
4. Fill in exception request:
   - Policy: "Maximum Liability Cap"
   - Violation: "Liability exceeds $1M"
   - Reason: "Strategic vendor, acceptable business risk"
   - Valid until: 90 days from now
5. Submit request
6. **Expected Result**:
   - Request created successfully
   - Status shows "Pending Approval"
   - Approver receives notification
   - Request appears in pending exceptions list
   - Cannot finalize contract until approved

### Use Case 9.2: Approve/Reject Exception (Approver Role)
**Goal**: Review and approve exception request

**Test Flow**:
1. Log in as user with Approver role
2. Navigate to Approvals > Pending Exceptions
3. Review exception request details
4. View associated contract and violation
5. Click "Approve" (or "Reject")
6. Add approval notes (optional)
7. Confirm decision
8. **Expected Result**:
   - Exception status updated to "Approved" or "Rejected"
   - Requestor receives notification
   - If approved:
     - Contract can proceed to finalization
     - Exception tracked with expiration date
   - If rejected:
     - Rejection reason logged
     - Contract returns to review state

---

## 10. Contract Finalization Feature

### Use Case 10.1: Finalize Approved Contract
**Goal**: Complete approval and generate final PDF

**Test Flow**:
1. Ensure all exceptions approved (if any)
2. Navigate to contract details
3. Click "Finalize Contract" button
4. Review final contract summary
5. Confirm finalization
6. Download finalized PDF
7. **Expected Result**:
   - Contract status changes to "Finalized"
   - Finalization timestamp recorded
   - PDF generated with approval stamps
   - All exception details included
   - Audit trail complete
   - Email notification sent to stakeholders

### Use Case 10.2: Attempt Finalization with Pending Violations
**Goal**: Verify cannot finalize with unresolved issues

**Test Flow**:
1. Upload contract with policy violations
2. Run Risk Agent (violations detected)
3. Do NOT request exceptions
4. Attempt to click "Finalize Contract"
5. **Expected Result**:
   - Finalize button disabled or shows error
   - Warning message: "Cannot finalize contract with pending violations"
   - Lists unresolved violations
   - Prompts to either:
     - Request exceptions
     - Modify contract to resolve violations
   - No PDF generated

---

## Test Execution Checklist

### Pre-Testing Setup
- [ ] Backend deployed and healthy (all pods running)
- [ ] Frontend deployed to Vercel
- [ ] Database migrations applied
- [ ] Test documents prepared (variety of contract types)
- [ ] Test user accounts created (standard user + approver role)
- [ ] Slack webhooks configured for notifications

### Testing Phases

#### Phase 1: Core Document Management
- [ ] Use Case 1.1: Single document upload
- [ ] Use Case 1.2: Batch document upload
- [ ] Verify document list, search, and filtering

#### Phase 2: AI Agent Functionality
- [ ] Use Case 2.1: Extract agent - employment contract
- [ ] Use Case 2.2: Extract agent - multi-party agreement
- [ ] Use Case 3.1: Risk agent - vendor contract
- [ ] Use Case 3.2: Risk agent - NDA compliance
- [ ] Use Case 4.1: Comparison agent - version diff
- [ ] Use Case 4.2: Comparison agent - vendor comparison
- [ ] Use Case 5.1: Q&A agent - payment terms
- [ ] Use Case 5.2: Q&A agent - termination conditions

#### Phase 3: Advanced Features
- [ ] Use Case 6.1: Create SaaS specialist agent
- [ ] Use Case 6.2: Create lease analyzer agent
- [ ] Use Case 7.1: Create liability cap policy
- [ ] Use Case 7.2: Upload policy document

#### Phase 4: Integrations & Workflows
- [ ] Use Case 8.1: Configure risk alert notifications
- [ ] Use Case 8.2: Configure intake notifications
- [ ] Use Case 9.1: Request policy exception
- [ ] Use Case 9.2: Approve/reject exception
- [ ] Use Case 10.1: Finalize approved contract
- [ ] Use Case 10.2: Block finalization with violations

### Bug Tracking Template

| Test Case | Status | Issue | Severity | Notes |
|-----------|--------|-------|----------|-------|
| 1.1 | ✅ Pass / ❌ Fail | Description | High/Med/Low | Details |
| 1.2 | | | | |
| ... | | | | |

### Success Criteria
- All 20 use cases pass without errors
- No console errors in browser
- API response times < 3 seconds (except AI agents)
- AI agent accuracy > 85% on test documents
- All notifications delivered successfully
- Proper error handling for edge cases

---

## Notes for Tester

1. **Browser**: Test in latest Chrome, Firefox, and Safari
2. **Network**: Test with both fast and throttled connections
3. **Error Scenarios**: Try invalid inputs, large files, timeout scenarios
4. **Security**: Verify users can only access their org's documents
5. **Performance**: Note any slow loading or laggy interactions
6. **Mobile**: Verify responsive design on tablet/mobile (bonus)

---

**Document Version**: 1.0
**Last Updated**: 2026-06-16
**Created By**: Claude (AI Assistant)
