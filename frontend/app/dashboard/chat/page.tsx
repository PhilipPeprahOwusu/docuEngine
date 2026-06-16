'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Bot,
  Send,
  FileText,
  Loader2,
  User,
  Sparkles,
  Database,
  AlertCircle
} from 'lucide-react';
import { documentAPI } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { documentId: string; chunk: string; page?: number }[];
  timestamp: Date;
}

interface Document {
  id: string;
  filename: string;
}

export default function ChatPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        'Hello! I\'m your AI contract intelligence assistant. I can help you understand, analyze, and extract information from your contracts. Select documents below to get started, then ask me anything!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    'What are the payment terms in this contract?',
    'Identify all parties involved in this agreement',
    'What are the termination clauses?',
    'Are there any liability limitations?',
    'Summarize the key obligations',
    'What are the renewal terms?',
  ];

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadDocuments = async () => {
    try {
      const response = await documentAPI.list();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const toggleDocument = (docId: string) => {
    setSelectedDocs((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || loading) return;

    if (selectedDocs.length === 0) {
      alert('Please select at least one document for context');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Simulate RAG-powered response
      // In production, this would call your backend RAG endpoint
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Based on the contract analysis using RAG pipeline across ${selectedDocs.length} document(s):\n\n${generateMockResponse(messageText)}`,
        sources: [
          {
            documentId: selectedDocs[0],
            chunk: 'Sample relevant text from the contract...',
            page: 3,
          },
        ],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to process your question'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const generateMockResponse = (question: string): string => {
    const lower = question.toLowerCase();

    if (lower.includes('payment') || lower.includes('term')) {
      return 'The contract specifies monthly payments of $10,000 due on the first business day of each month. Payment terms include:\n\n• Net 30 payment schedule\n• Late payment fee of 1.5% per month\n• Wire transfer to designated account\n• Invoice required 5 business days prior to payment\n\nAll payments are subject to standard audit and verification procedures as outlined in Section 4.2.';
    }

    if (lower.includes('parties') || lower.includes('involved')) {
      return 'The following parties are identified in this agreement:\n\n**Primary Parties:**\n• Acme Corporation (Client) - headquartered in Delaware\n• Global Services Inc. (Provider) - incorporated in California\n\n**Additional Stakeholders:**\n• TechStart Ventures LLC - as guarantor\n• First National Bank - as escrow agent\n\nEach party\'s rights, obligations, and contact information are detailed in Exhibit A.';
    }

    if (lower.includes('termination') || lower.includes('cancel')) {
      return 'Termination provisions include:\n\n**Termination for Convenience:** Either party may terminate with 90 days written notice.\n\n**Termination for Cause:** Immediate termination allowed if:\n• Material breach not cured within 30 days\n• Bankruptcy or insolvency\n• Regulatory compliance failure\n\n**Exit Obligations:**\n• Data return within 45 days\n• Knowledge transfer period of 60 days\n• Final payment settlement\n\nTermination does not affect accrued rights or obligations per Section 12.4.';
    }

    if (lower.includes('liability') || lower.includes('limitation')) {
      return 'Liability limitations are structured as follows:\n\n**Cap:** Total liability limited to fees paid in preceding 12 months, except for:\n• Gross negligence or willful misconduct\n• Breach of confidentiality\n• Intellectual property infringement\n\n**Excluded Damages:** No liability for consequential, indirect, or punitive damages.\n\n**Insurance:** Provider maintains $5M professional liability coverage.\n\nIndemnification obligations are mutual and detailed in Section 9.';
    }

    if (lower.includes('summarize') || lower.includes('key') || lower.includes('obligation')) {
      return '**Key Contract Obligations:**\n\n**Provider Obligations:**\n• Deliver services per SOW specifications\n• Maintain 99.9% uptime SLA\n• Provide monthly reporting\n• Ensure data security compliance\n• Assign qualified personnel\n\n**Client Obligations:**\n• Timely payment as agreed\n• Provide necessary access and information\n• Designate project manager\n• Review deliverables within 10 business days\n• Maintain confidentiality\n\nBoth parties must comply with all applicable laws and regulations.';
    }

    if (lower.includes('renewal') || lower.includes('renew')) {
      return 'Renewal terms are as follows:\n\n**Initial Term:** 36 months from effective date\n\n**Automatic Renewal:** Contract renews automatically for successive 12-month periods unless either party provides 90 days written notice.\n\n**Pricing Adjustment:** Annual increase not to exceed 5% or CPI, whichever is lower.\n\n**Renegotiation:** Either party may request terms renegotiation 120 days before renewal.\n\n**Termination Window:** 30-day window after each renewal to terminate without penalty.';
    }

    return `I've analyzed the contract using semantic search across the selected documents. The information you're looking for relates to:\n\n• Contractual framework and structure\n• Rights and obligations of parties\n• Compliance and regulatory requirements\n• Risk allocation mechanisms\n\nFor more specific details, please refine your question or ask about particular sections, clauses, or terms you'd like me to examine more closely.`;
  };

  return (
    <div className="grid h-[calc(100vh-12rem)] gap-6 lg:grid-cols-[300px_1fr]">
      {/* Document Selection Sidebar */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Document Context
          </CardTitle>
          <CardDescription>
            Select documents for RAG-powered chat
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-2">
          {documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <AlertCircle className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                No documents uploaded yet. Upload documents to start chatting.
              </p>
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className={`flex items-start gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedDocs.includes(doc.id)
                    ? 'border-gray-400 bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleDocument(doc.id)}
              >
                <input
                  type="checkbox"
                  checked={selectedDocs.includes(doc.id)}
                  onChange={() => toggleDocument(doc.id)}
                  className="mt-1"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 flex-shrink-0" />
                    <p className="text-sm font-medium truncate">{doc.filename}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </CardContent>
        {selectedDocs.length > 0 && (
          <div className="p-4 border-t">
            <Badge variant="default" className="w-full justify-center">
              <Sparkles className="h-3 w-3 mr-1" />
              {selectedDocs.length} document(s) selected
            </Badge>
          </div>
        )}
      </Card>

      {/* Chat Interface */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>Contract Intelligence Chat</CardTitle>
          <CardDescription>
            Ask questions about your contracts with RAG-powered responses
          </CardDescription>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-gray-700" />
                </div>
              )}
              <div
                className={`flex flex-col max-w-[80%] ${
                  message.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    <span className="font-medium">Sources:</span> Page {message.sources[0].page}
                  </div>
                )}
                <span className="text-xs text-muted-foreground mt-1">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="h-5 w-5 text-gray-600" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <Bot className="h-5 w-5 text-gray-700" />
              </div>
              <div className="flex items-center gap-2 bg-gray-100 rounded-lg px-4 py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Analyzing contracts...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </CardContent>

        {/* Suggested Questions */}
        {messages.length === 1 && (
          <div className="px-6 pb-4">
            <p className="text-sm font-medium mb-2">Suggested questions:</p>
            <div className="grid grid-cols-2 gap-2">
              {suggestedQuestions.slice(0, 4).map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(question)}
                  className="text-left text-xs p-2 rounded border hover:bg-gray-50 transition-colors"
                  disabled={loading || selectedDocs.length === 0}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-6 border-t">
          <div className="flex gap-2">
            <Textarea
              placeholder="Ask about payment terms, parties, obligations, risks..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              rows={2}
              className="resize-none"
              disabled={loading}
            />
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading || selectedDocs.length === 0}
              size="icon"
              className="h-full aspect-square"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          {selectedDocs.length === 0 && (
            <p className="text-xs text-muted-foreground mt-2">
              Select documents to enable chat
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
