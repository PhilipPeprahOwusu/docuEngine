'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  BookOpen,
  Plus,
  TrendingUp,
  TrendingDown,
  Minus,
  CheckCircle2,
  AlertTriangle,
  Info,
  Edit,
  Download
} from 'lucide-react';

export default function PlaybooksPage() {
  const [selectedPlaybook, setSelectedPlaybook] = useState<string | null>(null);

  const playbooks = [
    {
      id: '1',
      name: 'SaaS Vendor Negotiation',
      description: 'Standard playbook for negotiating with SaaS vendors',
      category: 'Procurement',
      status: 'active',
      usageCount: 24,
      successRate: 87,
      avgSavings: '$45K',
      lastUpdated: '2024-01-20',
      clauses: [
        {
          clause: 'Payment Terms',
          position: 'firm',
          guidance: 'Net 45 required. Do not accept Net 30 unless 5% discount offered.',
          fallback: 'Net 30 with 3% discount acceptable',
          priority: 'high',
        },
        {
          clause: 'Auto-Renewal',
          position: 'negotiable',
          guidance: 'Prefer opt-in renewal. If auto-renewal, require 120-day notice period minimum.',
          fallback: '90-day notice acceptable for multi-year contracts',
          priority: 'high',
        },
        {
          clause: 'Data Ownership',
          position: 'non-negotiable',
          guidance: 'Customer must retain full ownership of all data. No exceptions.',
          fallback: 'None - this is non-negotiable',
          priority: 'critical',
        },
        {
          clause: 'Price Escalation',
          position: 'firm',
          guidance: 'Cap annual increases at 3% or CPI, whichever is lower.',
          fallback: '5% cap acceptable for 3+ year terms',
          priority: 'medium',
        },
        {
          clause: 'Termination Rights',
          position: 'firm',
          guidance: 'Must include termination for convenience with 90-day notice.',
          fallback: '60-day notice acceptable',
          priority: 'medium',
        },
      ],
    },
    {
      id: '2',
      name: 'Enterprise Customer Contracts',
      description: 'Guidelines for negotiating with enterprise customers',
      category: 'Sales',
      status: 'active',
      usageCount: 18,
      successRate: 92,
      avgSavings: '$120K',
      lastUpdated: '2024-01-15',
      clauses: [
        {
          clause: 'Service Level Agreement',
          position: 'negotiable',
          guidance: '99.9% uptime standard. Consider 99.95% for enterprise tier only.',
          fallback: 'Credits limited to 10% monthly fees',
          priority: 'high',
        },
        {
          clause: 'Liability Cap',
          position: 'firm',
          guidance: 'Cap at 12 months fees. Resist uncapped liability requests.',
          fallback: '18 months fees for 3+ year contracts',
          priority: 'critical',
        },
        {
          clause: 'Indemnification',
          position: 'firm',
          guidance: 'Mutual indemnification only. Resist one-sided indemnity.',
          fallback: 'Broader scope acceptable if reciprocal',
          priority: 'high',
        },
      ],
    },
    {
      id: '3',
      name: 'Professional Services Agreements',
      description: 'Framework for services engagement negotiations',
      category: 'Services',
      status: 'active',
      usageCount: 32,
      successRate: 85,
      avgSavings: '$30K',
      lastUpdated: '2024-01-18',
      clauses: [
        {
          clause: 'Scope Changes',
          position: 'firm',
          guidance: 'All scope changes require written change order. No exceptions.',
          fallback: 'Minor changes (<5% fee impact) via email acceptable',
          priority: 'high',
        },
        {
          clause: 'Payment Schedule',
          position: 'negotiable',
          guidance: 'Prefer milestone-based payments. Minimum 30% upfront.',
          fallback: 'Monthly billing acceptable for long-term engagements',
          priority: 'medium',
        },
        {
          clause: 'IP Ownership',
          position: 'non-negotiable',
          guidance: 'Work product ownership transfers upon final payment only.',
          fallback: 'None - protect IP until paid',
          priority: 'critical',
        },
      ],
    },
  ];

  const getPositionIcon = (position: string) => {
    switch (position) {
      case 'firm':
        return <TrendingDown className="h-4 w-4 text-yellow-600" />;
      case 'negotiable':
        return <Minus className="h-4 w-4 text-gray-700" />;
      case 'non-negotiable':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'firm':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'negotiable':
        return 'bg-gray-50 border-gray-200 text-gray-900';
      case 'non-negotiable':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'default';
      case 'medium':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Negotiation Playbooks</h1>
          <p className="text-muted-foreground">
            Strategic guidance for contract negotiations based on company policies
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Create Playbook
        </Button>
      </div>

      {/* Playbook Cards */}
      <div className="grid gap-4">
        {playbooks.map((playbook) => (
          <Card
            key={playbook.id}
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedPlaybook === playbook.id ? 'ring-2 ring-gray-400' : ''
            }`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="h-5 w-5 text-muted-foreground" />
                    <CardTitle>{playbook.name}</CardTitle>
                    <Badge variant={playbook.status === 'active' ? 'default' : 'secondary'}>
                      {playbook.status}
                    </Badge>
                    <Badge variant="outline">{playbook.category}</Badge>
                  </div>
                  <CardDescription>{playbook.description}</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Stats */}
              <div className="flex gap-6 mt-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Usage:</span>
                  <span className="font-semibold ml-2">{playbook.usageCount} contracts</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Success Rate:</span>
                  <span className="font-semibold ml-2 text-green-600">{playbook.successRate}%</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Avg Savings:</span>
                  <span className="font-semibold ml-2 text-gray-700">{playbook.avgSavings}</span>
                </div>
                <div className="ml-auto text-muted-foreground">
                  Updated: {new Date(playbook.lastUpdated).toLocaleDateString()}
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold">Negotiation Guidance</h4>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      setSelectedPlaybook(selectedPlaybook === playbook.id ? null : playbook.id)
                    }
                  >
                    {selectedPlaybook === playbook.id ? 'Hide Details' : 'Show Details'}
                  </Button>
                </div>

                {selectedPlaybook === playbook.id ? (
                  <div className="space-y-3">
                    {playbook.clauses.map((item, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg border-2 ${getPositionColor(item.position)}`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getPositionIcon(item.position)}
                            <h5 className="font-semibold text-sm">{item.clause}</h5>
                          </div>
                          <div className="flex gap-2">
                            <Badge variant={getPriorityColor(item.priority) as any} className="text-xs">
                              {item.priority}
                            </Badge>
                            <Badge variant="outline" className="text-xs capitalize">
                              {item.position}
                            </Badge>
                          </div>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="font-medium">Guidance: </span>
                            <span>{item.guidance}</span>
                          </div>
                          <div className="pl-4 border-l-2 border-current opacity-70">
                            <span className="font-medium">Fallback: </span>
                            <span className="italic">{item.fallback}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-3 gap-2">
                    {playbook.clauses.slice(0, 6).map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-2 rounded border bg-gray-50 text-xs"
                      >
                        {getPositionIcon(item.position)}
                        <span className="truncate">{item.clause}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Negotiation Position Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
              <div>
                <p className="font-semibold">Non-Negotiable</p>
                <p className="text-xs text-muted-foreground">
                  Hard requirements - do not compromise
                </p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <TrendingDown className="h-4 w-4 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-semibold">Firm</p>
                <p className="text-xs text-muted-foreground">
                  Preferred position - fallback available
                </p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Minus className="h-4 w-4 text-gray-700 mt-0.5" />
              <div>
                <p className="font-semibold">Negotiable</p>
                <p className="text-xs text-muted-foreground">
                  Flexible - optimize based on priorities
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
