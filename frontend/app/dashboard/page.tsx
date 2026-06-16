'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import Link from 'next/link';
import {
  FileText,
  Bot,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Upload,
  ArrowRight,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
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

  const analysisProgress = stats.totalDocuments > 0
    ? Math.round((stats.analyzedDocuments / stats.totalDocuments) * 100)
    : 0;

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your documents.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
              <FileText className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="secondary" className="text-xs">
                <TrendingUp className="h-3 w-3 mr-1" />
                +12% from last month
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Analyzed</CardTitle>
            <div className="h-8 w-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
              <Bot className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.analyzedDocuments}</div>
            <div className="space-y-2 mt-2">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{analysisProgress}% processed</span>
                <span>{stats.totalDocuments - stats.analyzedDocuments} pending</span>
              </div>
              <Progress value={analysisProgress} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
            <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
              <ShieldCheck className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activePolicies}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Compliance rules enforced
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Violations</CardTitle>
            <div className="h-8 w-8 rounded-full bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
              <AlertCircle className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.violations}</div>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline" className="text-xs text-green-600 border-green-600">
                <TrendingDown className="h-3 w-3 mr-1" />
                -5% from last week
              </Badge>
            </div>
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

      {/* Recent Activity & Getting Started */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard/documents">
                  View all <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            </div>
            <CardDescription>Your latest document actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.totalDocuments === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No recent activity yet</p>
                  <p className="text-sm">Upload a document to get started</p>
                </div>
              ) : (
                <>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-4 w-4 text-blue-600 dark:text-blue-300" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">Document Uploaded</p>
                      <p className="text-xs text-muted-foreground">
                        SaaS Agreement.pdf • 2 hours ago
                      </p>
                    </div>
                    <Badge variant="secondary">New</Badge>
                  </div>
                  <Separator />
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-purple-600 dark:text-purple-300" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">AI Analysis Completed</p>
                      <p className="text-xs text-muted-foreground">
                        Extract Agent • 3 hours ago
                      </p>
                    </div>
                    <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0" />
                  </div>
                  <Separator />
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center flex-shrink-0">
                      <ShieldCheck className="h-4 w-4 text-green-600 dark:text-green-300" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">Policy Updated</p>
                      <p className="text-xs text-muted-foreground">
                        Liability Cap Policy • 1 day ago
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              Quick guide to using your Document Intelligence Platform
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 font-semibold flex-shrink-0">
                1
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium">Upload Your First Document</h4>
                <p className="text-sm text-muted-foreground">
                  Go to Documents and upload a contract, policy, or report for analysis
                </p>
              </div>
            </div>
            <Separator />
            <div className="flex items-start gap-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 font-semibold flex-shrink-0">
                2
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium">Run AI Analysis</h4>
                <p className="text-sm text-muted-foreground">
                  Use AI agents to extract information, assess risks, and get instant answers
                </p>
              </div>
            </div>
            <Separator />
            <div className="flex items-start gap-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 font-semibold flex-shrink-0">
                3
              </div>
              <div className="flex-1 space-y-1">
                <h4 className="font-medium">Set Up Policies</h4>
                <p className="text-sm text-muted-foreground">
                  Create custom policies to automatically check documents for compliance
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
