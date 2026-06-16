'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Bot,
  FileSearch,
  Shield,
  GitCompare,
  MessageSquare,
  Loader2,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import { documentAPI, agentAPI } from '@/lib/api';

interface Document {
  id: string;
  filename: string;
  document_type: string;
}

export default function AnalysisPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string>('');
  const [selectedDoc2, setSelectedDoc2] = useState<string>('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentAPI.list();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const runExtract = async () => {
    if (!selectedDoc) return;

    setLoading(true);
    setActiveAgent('extract');
    setResults(null);

    try {
      const response = await agentAPI.extract(selectedDoc);
      setResults(response.data);
    } catch (error: any) {
      setResults({ error: error.response?.data?.detail || 'Extraction failed' });
    } finally {
      setLoading(false);
    }
  };

  const runRisk = async () => {
    if (!selectedDoc) return;

    setLoading(true);
    setActiveAgent('risk');
    setResults(null);

    try {
      const response = await agentAPI.risk(selectedDoc);
      setResults(response.data);
    } catch (error: any) {
      setResults({ error: error.response?.data?.detail || 'Risk assessment failed' });
    } finally {
      setLoading(false);
    }
  };

  const runCompare = async () => {
    if (!selectedDoc || !selectedDoc2) return;

    setLoading(true);
    setActiveAgent('compare');
    setResults(null);

    try {
      const response = await agentAPI.compare(selectedDoc, selectedDoc2);
      setResults(response.data);
    } catch (error: any) {
      setResults({ error: error.response?.data?.detail || 'Comparison failed' });
    } finally {
      setLoading(false);
    }
  };

  const runQA = async () => {
    if (!selectedDoc || !question.trim()) return;

    setLoading(true);
    setActiveAgent('qa');
    setResults(null);

    try {
      const response = await agentAPI.qa(selectedDoc, question);
      setResults(response.data);
    } catch (error: any) {
      setResults({ error: error.response?.data?.detail || 'Q&A failed' });
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    if (results.error) {
      return (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-800">{results.error}</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {activeAgent === 'extract' && (
          <div className="space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Extracted Information
            </h3>
            <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
              {JSON.stringify(results.extraction, null, 2)}
            </pre>
          </div>
        )}

        {activeAgent === 'risk' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <Shield className="h-5 w-5 text-gray-700" />
                Risk Assessment
              </h3>
              <Badge variant={results.compliance_score > 70 ? 'default' : 'destructive'}>
                Score: {results.compliance_score}%
              </Badge>
            </div>
            <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
              {JSON.stringify(results.risks, null, 2)}
            </pre>
          </div>
        )}

        {activeAgent === 'compare' && (
          <div className="space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <GitCompare className="h-5 w-5 text-purple-600" />
              Document Comparison
            </h3>
            <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
              {JSON.stringify(results.comparison, null, 2)}
            </pre>
          </div>
        )}

        {activeAgent === 'qa' && (
          <div className="space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-orange-600" />
              Answer
            </h3>
            <div className="rounded-lg bg-slate-100 p-4">
              <p className="text-sm text-muted-foreground mb-2">Q: {results.question}</p>
              <p className="text-sm">{results.answer}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">AI Analysis</h1>
        <p className="text-muted-foreground">
          Use AI agents to extract data, assess risks, compare documents, and answer questions
        </p>
      </div>

      {/* Agent Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Extract Agent */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSearch className="h-5 w-5" />
              Extract Information
            </CardTitle>
            <CardDescription>
              Extract structured data from contracts and documents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              disabled={loading}
            >
              <option value="">Select a document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <Button
              onClick={runExtract}
              disabled={!selectedDoc || loading}
              className="w-full"
            >
              {loading && activeAgent === 'extract' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  Run Extract Agent
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Risk Agent */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Risk Assessment
            </CardTitle>
            <CardDescription>
              Identify risks and compliance issues in documents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              disabled={loading}
            >
              <option value="">Select a document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <Button
              onClick={runRisk}
              disabled={!selectedDoc || loading}
              className="w-full"
            >
              {loading && activeAgent === 'risk' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  Run Risk Agent
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Compare Agent */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitCompare className="h-5 w-5" />
              Compare Documents
            </CardTitle>
            <CardDescription>
              Compare two documents to identify differences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              disabled={loading}
            >
              <option value="">Select first document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <select
              value={selectedDoc2}
              onChange={(e) => setSelectedDoc2(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              disabled={loading}
            >
              <option value="">Select second document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <Button
              onClick={runCompare}
              disabled={!selectedDoc || !selectedDoc2 || loading}
              className="w-full"
            >
              {loading && activeAgent === 'compare' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  Run Compare Agent
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Q&A Agent */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Ask Questions
            </CardTitle>
            <CardDescription>
              Ask questions about your documents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              disabled={loading}
            >
              <option value="">Select a document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <Textarea
              placeholder="What is the payment term? Who are the parties? What are the key clauses?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
              rows={3}
            />
            <Button
              onClick={runQA}
              disabled={!selectedDoc || !question.trim() || loading}
              className="w-full"
            >
              {loading && activeAgent === 'qa' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Thinking...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  Ask Question
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Results */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>{renderResults()}</CardContent>
        </Card>
      )}
    </div>
  );
}
