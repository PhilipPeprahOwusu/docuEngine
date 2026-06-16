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
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-800 mb-1">Analysis Failed</p>
              <p className="text-sm text-red-700">{results.error}</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {activeAgent === 'extract' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <h3 className="text-xl font-semibold">Extracted Information</h3>
            </div>

            {/* Display extracted data as structured cards */}
            {results.extraction && typeof results.extraction === 'object' ? (
              <div className="grid gap-4 md:grid-cols-2">
                {Object.entries(results.extraction).map(([key, value]) => (
                  <Card key={key}>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium text-muted-foreground capitalize">
                        {key.replace(/_/g, ' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-base font-semibold">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
                {JSON.stringify(results.extraction, null, 2)}
              </pre>
            )}
          </div>
        )}

        {activeAgent === 'risk' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Shield className="h-6 w-6 text-gray-700" />
                <h3 className="text-xl font-semibold">Risk Assessment</h3>
              </div>
              <Badge
                variant={results.compliance_score > 70 ? 'default' : 'destructive'}
                className="text-lg px-4 py-1"
              >
                Score: {results.compliance_score}%
              </Badge>
            </div>

            {/* Display risks as cards */}
            {results.risks && typeof results.risks === 'object' ? (
              <div className="space-y-3">
                {Object.entries(results.risks).map(([category, items]: [string, any]) => (
                  <Card key={category} className="border-l-4 border-l-yellow-500">
                    <CardHeader>
                      <CardTitle className="text-base capitalize flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-yellow-600" />
                        {category.replace(/_/g, ' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {Array.isArray(items) ? (
                        <ul className="space-y-2">
                          {items.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm">
                              <span className="text-yellow-600 mt-0.5">•</span>
                              <span>{typeof item === 'object' ? JSON.stringify(item) : String(item)}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm">{String(items)}</p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
                {JSON.stringify(results.risks, null, 2)}
              </pre>
            )}
          </div>
        )}

        {activeAgent === 'compare' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <GitCompare className="h-6 w-6 text-purple-600" />
              <h3 className="text-xl font-semibold">Document Comparison</h3>
            </div>

            {/* Display comparison as structured diff */}
            {results.comparison && typeof results.comparison === 'object' ? (
              <div className="space-y-3">
                {Object.entries(results.comparison).map(([section, diff]: [string, any]) => (
                  <Card key={section}>
                    <CardHeader>
                      <CardTitle className="text-base capitalize">
                        {section.replace(/_/g, ' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm space-y-2">
                        {typeof diff === 'object' ? (
                          Object.entries(diff).map(([key, value]) => (
                            <div key={key} className="flex gap-2">
                              <span className="font-medium min-w-24 capitalize">
                                {key.replace(/_/g, ' ')}:
                              </span>
                              <span className="text-muted-foreground">{String(value)}</span>
                            </div>
                          ))
                        ) : (
                          <span>{String(diff)}</span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <pre className="rounded-lg bg-slate-100 p-4 overflow-auto text-sm">
                {JSON.stringify(results.comparison, null, 2)}
              </pre>
            )}
          </div>
        )}

        {activeAgent === 'qa' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="h-6 w-6 text-orange-600" />
              <h3 className="text-xl font-semibold">Q&A Response</h3>
            </div>

            <Card className="border-l-4 border-l-orange-500">
              <CardHeader className="bg-slate-50">
                <div className="flex items-start gap-2">
                  <MessageSquare className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <p className="text-sm font-medium">Question:</p>
                </div>
                <p className="text-base mt-2">{results.question}</p>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="flex items-start gap-2 mb-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <p className="text-sm font-medium">Answer:</p>
                </div>
                <p className="text-base leading-relaxed">{results.answer}</p>
              </CardContent>
            </Card>
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
