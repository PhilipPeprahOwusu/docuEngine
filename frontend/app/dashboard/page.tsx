'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { FileText, Bot, ShieldCheck, TrendingUp, Upload, ArrowRight } from 'lucide-react';
import { documentAPI, policyAPI } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalDocuments: 0,
    analyzedDocuments: 0,
    activePolicies: 0,
    violations: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load documents
      const documentsRes = await documentAPI.list();

      // Try to load policies, but don't fail if endpoint doesn't exist
      let policiesCount = 0;
      try {
        const policiesRes = await policyAPI.list();
        policiesCount = policiesRes.data?.length || 0;
      } catch (err) {
        console.log('Policies endpoint not yet implemented');
      }

      setStats({
        totalDocuments: documentsRes.data?.length || 0,
        analyzedDocuments: documentsRes.data?.filter((d: any) => d.analysis_status === 'completed')?.length || 0,
        activePolicies: policiesCount,
        violations: 0, // We'll implement this later
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            <p className="text-xs text-muted-foreground">Documents uploaded</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Analyzed</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.analyzedDocuments}</div>
            <p className="text-xs text-muted-foreground">Processed by AI</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activePolicies}</div>
            <p className="text-xs text-muted-foreground">Compliance rules</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Violations</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.violations}</div>
            <p className="text-xs text-muted-foreground">Policy breaches</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Upload a new document for AI-powered analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/documents">
              <Button className="w-full">
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Analysis</CardTitle>
            <CardDescription>
              Analyze documents with AI agents for insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/analysis">
              <Button variant="outline" className="w-full">
                <Bot className="mr-2 h-4 w-4" />
                Start Analysis
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            Quick guide to using your Document Intelligence Platform
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-700">
              1
            </div>
            <div className="flex-1">
              <h4 className="font-medium">Upload Your First Document</h4>
              <p className="text-sm text-muted-foreground">
                Go to Documents and upload a contract, policy, or report for analysis
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-700">
              2
            </div>
            <div className="flex-1">
              <h4 className="font-medium">Run AI Analysis</h4>
              <p className="text-sm text-muted-foreground">
                Use AI agents to extract information, assess risks, and get instant answers
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-700">
              3
            </div>
            <div className="flex-1">
              <h4 className="font-medium">Set Up Policies</h4>
              <p className="text-sm text-muted-foreground">
                Create custom policies to automatically check documents for compliance
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
