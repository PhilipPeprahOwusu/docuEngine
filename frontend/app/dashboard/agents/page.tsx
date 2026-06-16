'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Plus,
  Settings,
  Play,
  Edit,
  Trash2,
  FileSearch,
  Shield,
  GitCompare,
  MessageSquare,
  FileEdit,
  Zap
} from 'lucide-react';
import { agentAPI } from '@/lib/api';

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    system_prompt: '',
    temperature: 0.7,
    max_tokens: 4000,
    capabilities: [] as string[],
  });

  const builtInAgents = [
    {
      id: 'extract',
      name: 'Information Extractor',
      description: 'Extract structured data from contracts and legal documents',
      icon: FileSearch,
      color: 'text-gray-700',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      capabilities: ['Entity extraction', 'Key-value pairs', 'Date parsing', 'Party identification'],
      model: 'Claude 3.5 Sonnet',
      lastRun: '2 hours ago',
    },
    {
      id: 'risk',
      name: 'Risk Assessor',
      description: 'Identify risks and compliance issues in legal documents',
      icon: Shield,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      capabilities: ['Risk scoring', 'Compliance check', 'Policy violation detection', 'Liability analysis'],
      model: 'Claude 3.5 Sonnet',
      lastRun: '5 hours ago',
    },
    {
      id: 'compare',
      name: 'Document Comparator',
      description: 'Compare multiple contracts and identify key differences',
      icon: GitCompare,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      capabilities: ['Diff analysis', 'Change tracking', 'Version comparison', 'Clause mapping'],
      model: 'Claude 3.5 Sonnet',
      lastRun: '1 day ago',
    },
    {
      id: 'qa',
      name: 'Q&A Assistant',
      description: 'Answer questions about contract terms and conditions',
      icon: MessageSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      capabilities: ['Natural language Q&A', 'Context retrieval', 'Citation generation', 'Multi-doc search'],
      model: 'Claude 3.5 Sonnet',
      lastRun: '30 minutes ago',
    },
  ];

  const customAgents = [
    {
      id: 'custom-1',
      name: 'SaaS Contract Reviewer',
      description: 'Specialized agent for reviewing SaaS subscription agreements',
      icon: FileEdit,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      capabilities: ['SaaS-specific terms', 'Pricing structure analysis', 'SLA verification', 'Auto-renewal detection'],
      model: 'GPT-4 Turbo',
      lastRun: '3 days ago',
      custom: true,
    },
    {
      id: 'custom-2',
      name: 'NDA Analyzer',
      description: 'Fast analysis of non-disclosure agreements',
      icon: Zap,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      capabilities: ['Confidentiality scope', 'Term duration', 'Exception clauses', 'Mutual vs unilateral'],
      model: 'Claude 3 Haiku',
      lastRun: '1 week ago',
      custom: true,
    },
  ];

  const allAgents = [...builtInAgents, ...customAgents];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Agents</h1>
          <p className="text-muted-foreground">
            Configure and deploy custom AI agents for contract intelligence
          </p>
        </div>
        <Button className="gap-2" onClick={() => setCreateModalOpen(true)}>
          <Plus className="h-4 w-4" />
          Create Custom Agent
        </Button>
      </div>

      {/* Built-in Agents */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Built-in Agents</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {builtInAgents.map((agent) => (
            <Card
              key={agent.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selectedAgent === agent.id ? 'ring-2 ring-gray-400' : ''
              }`}
              onClick={() => setSelectedAgent(agent.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className={`p-3 rounded-lg ${agent.bgColor} border ${agent.borderColor}`}>
                    <agent.icon className={`h-6 w-6 ${agent.color}`} />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost">
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardTitle className="mt-4">{agent.name}</CardTitle>
                <CardDescription>{agent.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.slice(0, 3).map((cap, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {cap}
                      </Badge>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{agent.capabilities.length - 3} more
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Model: {agent.model}</span>
                    <span>Last run: {agent.lastRun}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Custom Agents */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Custom Agents</h2>
          <span className="text-sm text-muted-foreground">
            {customAgents.length} custom agents
          </span>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {customAgents.map((agent) => (
            <Card
              key={agent.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selectedAgent === agent.id ? 'ring-2 ring-gray-400' : ''
              }`}
              onClick={() => setSelectedAgent(agent.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className={`p-3 rounded-lg ${agent.bgColor} border ${agent.borderColor}`}>
                    <agent.icon className={`h-6 w-6 ${agent.color}`} />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost">
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardTitle className="mt-4 flex items-center gap-2">
                  {agent.name}
                  <Badge variant="outline" className="text-xs">Custom</Badge>
                </CardTitle>
                <CardDescription>{agent.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.slice(0, 3).map((cap, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {cap}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Model: {agent.model}</span>
                    <span>Last run: {agent.lastRun}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Agent Configuration Panel */}
      {selectedAgent && (
        <Card>
          <CardHeader>
            <CardTitle>Agent Configuration</CardTitle>
            <CardDescription>
              Configure settings for {allAgents.find(a => a.id === selectedAgent)?.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">System Prompt</label>
              <textarea
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[120px]"
                placeholder="You are an expert contract analyst specializing in..."
                defaultValue="You are an expert contract analyst with deep knowledge of legal terminology, contract structures, and risk assessment. Analyze documents with precision and provide actionable insights."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Temperature</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.3"
                  className="w-full"
                />
                <span className="text-xs text-muted-foreground">0.3 (Focused)</span>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Max Tokens</label>
                <input
                  type="number"
                  defaultValue="4096"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Tools & Capabilities</label>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">Document Search</Badge>
                <Badge variant="outline">Entity Extraction</Badge>
                <Badge variant="outline">Policy Validation</Badge>
                <Badge variant="outline">Risk Scoring</Badge>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline">Cancel</Button>
              <Button>Save Configuration</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Agent Modal */}
      <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Create Custom AI Agent</DialogTitle>
            <DialogDescription>
              Build a custom AI agent tailored to your specific contract intelligence needs
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* Agent Name */}
            <div className="space-y-2">
              <Label htmlFor="agent-name">Agent Name</Label>
              <Input
                id="agent-name"
                placeholder="e.g., SaaS Contract Reviewer"
                value={newAgent.name}
                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="agent-description">Description</Label>
              <Input
                id="agent-description"
                placeholder="Brief description of what this agent does"
                value={newAgent.description}
                onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
              />
            </div>

            {/* System Prompt */}
            <div className="space-y-2">
              <Label htmlFor="agent-prompt">System Prompt</Label>
              <Textarea
                id="agent-prompt"
                placeholder="You are an AI agent specialized in..."
                rows={6}
                value={newAgent.system_prompt}
                onChange={(e) => setNewAgent({ ...newAgent, system_prompt: e.target.value })}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Define the agent's behavior, expertise, and instructions
              </p>
            </div>

            {/* Temperature */}
            <div className="space-y-2">
              <Label htmlFor="agent-temperature">
                Temperature: {newAgent.temperature}
              </Label>
              <input
                id="agent-temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={newAgent.temperature}
                onChange={(e) => setNewAgent({ ...newAgent, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Lower = more focused, Higher = more creative
              </p>
            </div>

            {/* Max Tokens */}
            <div className="space-y-2">
              <Label htmlFor="agent-tokens">Max Tokens</Label>
              <Input
                id="agent-tokens"
                type="number"
                min="100"
                max="8000"
                value={newAgent.max_tokens}
                onChange={(e) => setNewAgent({ ...newAgent, max_tokens: parseInt(e.target.value) })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateModalOpen(false)}
              disabled={creating}
            >
              Cancel
            </Button>
            <Button
              onClick={async () => {
                setCreating(true);
                try {
                  await agentAPI.createCustomAgent(newAgent);
                  setCreateModalOpen(false);
                  setNewAgent({
                    name: '',
                    description: '',
                    system_prompt: '',
                    temperature: 0.7,
                    max_tokens: 4000,
                    capabilities: [],
                  });
                  alert('Agent created successfully!');
                  // Optionally reload agents list here
                } catch (error) {
                  console.error('Failed to create agent:', error);
                  alert('Failed to create agent. Please try again.');
                } finally {
                  setCreating(false);
                }
              }}
              disabled={creating || !newAgent.name || !newAgent.system_prompt}
            >
              {creating ? 'Creating...' : 'Create Agent'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
