'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Upload,
  FileText,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Edit,
  Trash2,
  Download
} from 'lucide-react';

export default function PoliciesPage() {
  const [uploading, setUploading] = useState(false);

  const policies = [
    {
      id: '1',
      name: 'Payment Terms Policy',
      description: 'Standard payment terms and conditions for all contracts',
      type: 'Financial',
      status: 'active',
      rules: [
        'Net 30 payment terms required',
        'Late fees must not exceed 1.5% per month',
        'Payment method must be wire transfer or ACH',
      ],
      violations: 0,
      lastUpdated: '2024-01-15',
      documents: 2,
    },
    {
      id: '2',
      name: 'Data Privacy & GDPR Compliance',
      description: 'GDPR and data protection requirements for all agreements',
      type: 'Compliance',
      status: 'active',
      rules: [
        'Data processing agreement required',
        'Must include right to deletion clause',
        'Data breach notification within 72 hours',
        'EU data residency requirements',
      ],
      violations: 3,
      lastUpdated: '2024-01-20',
      documents: 5,
    },
    {
      id: '3',
      name: 'Liability Cap Standards',
      description: 'Maximum liability limits for service agreements',
      type: 'Risk Management',
      status: 'active',
      rules: [
        'Total liability capped at 12 months fees',
        'Excluded: IP infringement, confidentiality breach',
        'Insurance requirements: $5M minimum',
      ],
      violations: 1,
      lastUpdated: '2024-01-10',
      documents: 3,
    },
    {
      id: '4',
      name: 'Termination Clause Requirements',
      description: 'Standard termination provisions and notice periods',
      type: 'Operational',
      status: 'active',
      rules: [
        '90-day notice for convenience termination',
        '30-day cure period for material breach',
        'Data return within 45 days post-termination',
      ],
      violations: 0,
      lastUpdated: '2024-01-18',
      documents: 4,
    },
    {
      id: '5',
      name: 'IP Rights & Licensing',
      description: 'Intellectual property ownership and licensing standards',
      type: 'Legal',
      status: 'draft',
      rules: [
        'Clear IP ownership definition required',
        'License scope must be explicitly stated',
        'Derivative works ownership',
      ],
      violations: 0,
      lastUpdated: '2024-01-22',
      documents: 1,
    },
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    // Simulate upload
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setUploading(false);
    alert(`Policy document "${file.name}" uploaded successfully!`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Policy Management</h1>
          <p className="text-muted-foreground">
            Define and enforce company policies across all contracts
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2" onClick={() => document.getElementById('policy-upload')?.click()}>
            <Upload className="h-4 w-4" />
            Upload Policy Doc
            <input
              id="policy-upload"
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileUpload}
            />
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Policy
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Policies</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies.length}</div>
            <p className="text-xs text-muted-foreground">
              {policies.filter(p => p.status === 'active').length} active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Policy Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {policies.reduce((sum, p) => sum + p.documents, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Reference documents
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Violations Detected</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {policies.reduce((sum, p) => sum + p.violations, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all contracts
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94%</div>
            <p className="text-xs text-muted-foreground">
              +2% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Policies List */}
      <div className="space-y-4">
        {policies.map((policy) => (
          <Card key={policy.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <CardTitle>{policy.name}</CardTitle>
                    <Badge variant={policy.status === 'active' ? 'default' : 'secondary'}>
                      {policy.status}
                    </Badge>
                    <Badge variant="outline">{policy.type}</Badge>
                  </div>
                  <CardDescription>{policy.description}</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Policy Rules */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Policy Rules:</h4>
                  <ul className="space-y-1">
                    {policy.rules.map((rule, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <span className="text-green-600 mt-0.5">✓</span>
                        <span>{rule}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Policy Stats */}
                <div className="flex items-center gap-6 text-sm text-muted-foreground border-t pt-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span>{policy.documents} reference docs</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {policy.violations > 0 ? (
                      <>
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                        <span className="text-yellow-600">{policy.violations} violations</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <span className="text-green-600">No violations</span>
                      </>
                    )}
                  </div>
                  <div className="ml-auto">
                    Last updated: {new Date(policy.lastUpdated).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Upload Modal */}
      {uploading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-96">
            <CardHeader>
              <CardTitle>Uploading Policy Document</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-800"></div>
                <span>Processing document...</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
