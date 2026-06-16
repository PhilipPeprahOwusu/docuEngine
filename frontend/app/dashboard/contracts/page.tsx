'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  FileEdit,
  Wand2,
  Download,
  Save,
  Copy,
  Sparkles,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

export default function ContractsPage() {
  const [contractType, setContractType] = useState('saas');
  const [generating, setGenerating] = useState(false);
  const [generatedContract, setGeneratedContract] = useState('');
  const [requirements, setRequirements] = useState('');

  const contractTypes = [
    {
      id: 'saas',
      name: 'SaaS Subscription Agreement',
      description: 'Software-as-a-Service subscription contract',
      templates: 12,
    },
    {
      id: 'nda',
      name: 'Non-Disclosure Agreement',
      description: 'Mutual or unilateral confidentiality agreement',
      templates: 8,
    },
    {
      id: 'msa',
      name: 'Master Service Agreement',
      description: 'Framework agreement for ongoing services',
      templates: 6,
    },
    {
      id: 'sow',
      name: 'Statement of Work',
      description: 'Project-specific scope and deliverables',
      templates: 10,
    },
  ];

  const generateContract = async () => {
    setGenerating(true);
    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 3000));

    setGeneratedContract(`# SAAS SUBSCRIPTION AGREEMENT

This SaaS Subscription Agreement ("Agreement") is entered into as of [DATE] ("Effective Date") by and between:

**PROVIDER:** [Company Name], a [State] corporation with principal offices at [Address] ("Provider")

**CUSTOMER:** [Customer Name], a [State] corporation with principal offices at [Address] ("Customer")

## 1. SERVICES

1.1 **Service Description.** Provider agrees to provide Customer with access to its cloud-based software platform ("Service") as described in Exhibit A, subject to the terms and conditions of this Agreement.

1.2 **Service Level Agreement.** Provider will use commercially reasonable efforts to maintain Service availability of 99.9% uptime, calculated monthly, excluding scheduled maintenance.

${requirements ? `\n## CUSTOM REQUIREMENTS\n${requirements}\n` : ''}

## 2. SUBSCRIPTION AND FEES

2.1 **Subscription Term.** The initial subscription term is [12/24/36] months from the Effective Date ("Initial Term"), automatically renewing for successive [12]-month periods ("Renewal Terms") unless either party provides written notice of non-renewal at least 90 days prior to the end of the then-current term.

2.2 **Subscription Fees.** Customer will pay Provider the fees set forth in Exhibit B. All fees are due within 30 days of invoice date.

2.3 **Payment Terms.**
   - Net 30 payment terms
   - Late payments subject to 1.5% monthly interest
   - Annual price increases capped at 5% or CPI, whichever is lower

## 3. DATA AND SECURITY

3.1 **Data Ownership.** Customer retains all rights, title, and interest in Customer Data. Provider's use is limited to providing the Service.

3.2 **Security Measures.** Provider will maintain reasonable administrative, physical, and technical safeguards including:
   - SOC 2 Type II certification
   - Encryption in transit (TLS 1.3) and at rest (AES-256)
   - Annual third-party security audits
   - Role-based access controls

3.3 **Data Privacy.** Provider will comply with applicable data protection laws, including GDPR and CCPA. Provider will enter into a Data Processing Agreement if required.

## 4. INTELLECTUAL PROPERTY

4.1 **Service IP.** Provider retains all rights in the Service and Provider IP. Customer receives a non-exclusive, non-transferable license to use the Service during the Subscription Term.

4.2 **Customer IP.** Customer retains all rights in Customer Data and Customer IP. Provider receives a limited license to process Customer Data solely to provide the Service.

## 5. WARRANTIES AND DISCLAIMERS

5.1 **Service Warranty.** Provider warrants that the Service will perform substantially in accordance with the Documentation.

5.2 **DISCLAIMER.** EXCEPT AS EXPRESSLY PROVIDED HEREIN, THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## 6. LIMITATION OF LIABILITY

6.1 **Liability Cap.** Provider's total liability will not exceed the fees paid by Customer in the 12 months preceding the claim.

6.2 **Excluded Damages.** Neither party will be liable for indirect, incidental, consequential, special, or punitive damages.

6.3 **Exceptions.** The limitation does not apply to:
   - Gross negligence or willful misconduct
   - Breach of confidentiality
   - Intellectual property infringement
   - Indemnification obligations

## 7. CONFIDENTIALITY

7.1 **Confidential Information.** Each party will protect the other's Confidential Information using the same degree of care used to protect its own confidential information, but no less than reasonable care.

7.2 **Exceptions.** Confidentiality obligations do not apply to information that is publicly available, independently developed, or lawfully received from third parties.

## 8. TERMINATION

8.1 **Termination for Convenience.** Either party may terminate with 90 days written notice.

8.2 **Termination for Cause.** Either party may terminate if the other party materially breaches and fails to cure within 30 days of written notice.

8.3 **Effect of Termination.**
   - Customer access to Service terminates immediately
   - Provider will return or destroy Customer Data within 45 days
   - Accrued payment obligations survive termination
   - Confidentiality obligations survive for 5 years

## 9. GENERAL PROVISIONS

9.1 **Governing Law.** This Agreement is governed by the laws of [State] without regard to conflict of laws principles.

9.2 **Entire Agreement.** This Agreement constitutes the entire agreement and supersedes all prior understandings.

9.3 **Amendments.** This Agreement may only be amended in writing signed by both parties.

9.4 **Assignment.** Neither party may assign this Agreement without prior written consent.

## EXHIBITS

**Exhibit A:** Service Description
**Exhibit B:** Pricing and Fees
**Exhibit C:** Data Processing Agreement (if applicable)

---

**PROVIDER:**                      **CUSTOMER:**

By: _________________________      By: _________________________
Name:                              Name:
Title:                             Title:
Date:                              Date:

---

*🤖 Generated with AI Contract Assistant*
*⚠️ This is a starting point - review with legal counsel before use*`);

    setGenerating(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedContract);
    alert('Contract copied to clipboard!');
  };

  return (
    <div className="grid h-[calc(100vh-12rem)] gap-6 lg:grid-cols-[400px_1fr]">
      {/* Configuration Sidebar */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileEdit className="h-5 w-5" />
            Contract Drafting
          </CardTitle>
          <CardDescription>
            AI-powered contract generation with compliance built-in
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-4">
          {/* Contract Type Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Contract Type</label>
            <div className="space-y-2">
              {contractTypes.map((type) => (
                <div
                  key={type.id}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    contractType === type.id
                      ? 'border-gray-400 bg-gray-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setContractType(type.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-sm">{type.name}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{type.description}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {type.templates} templates
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Requirements Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Specific Requirements (Optional)
            </label>
            <Textarea
              placeholder="Enter specific terms, clauses, or requirements to include in the contract..."
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              rows={6}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Example: "Include auto-renewal clause with 60-day notice period" or "Add data residency requirement for EU"
            </p>
          </div>

          {/* Compliance Checks */}
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-gray-700" />
              Auto-Applied Policies
            </h4>
            <ul className="space-y-1 text-xs">
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                Payment Terms Policy
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                GDPR Compliance
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                Liability Cap Standards
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                IP Rights Protection
              </li>
            </ul>
          </div>

          {/* Generate Button */}
          <Button
            onClick={generateContract}
            disabled={generating}
            className="w-full gap-2"
            size="lg"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating Contract...
              </>
            ) : (
              <>
                <Wand2 className="h-4 w-4" />
                Generate Contract
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Contract Display */}
      <Card className="flex flex-col">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Generated Contract</CardTitle>
              <CardDescription>
                AI-drafted contract with compliance checks applied
              </CardDescription>
            </div>
            {generatedContract && (
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={copyToClipboard}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
                <Button size="sm" variant="outline">
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto">
          {!generatedContract ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <Sparkles className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Ready to Draft</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Select a contract type and optionally add specific requirements, then click
                "Generate Contract" to create an AI-drafted agreement with your company policies
                automatically applied.
              </p>
            </div>
          ) : (
            <div className="prose prose-sm max-w-none">
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-xs">
                  <p className="font-medium text-yellow-800 mb-1">Legal Review Required</p>
                  <p className="text-yellow-700">
                    This AI-generated contract is a starting point and should be reviewed by legal
                    counsel before use. Verify all terms align with your specific needs and
                    jurisdiction.
                  </p>
                </div>
              </div>
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                {generatedContract}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
