'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Save, Check, Send } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { notificationAPI } from '@/lib/api';

export default function SettingsPage() {
  const [selectedProvider, setSelectedProvider] = useState('anthropic');
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    gemini: '',
  });
  const [models, setModels] = useState({
    openai: 'gpt-4-turbo-preview',
    anthropic: 'claude-3-5-sonnet-20241022',
    gemini: 'gemini-pro',
  });
  const [slackWebhooks, setSlackWebhooks] = useState({
    riskAlerts: '',
    policyViolations: '',
    contractIntake: '',
    weeklyReports: '',
  });
  const [saved, setSaved] = useState(false);

  const providers = [
    {
      id: 'openai',
      name: 'OpenAI',
      description: 'GPT-4, GPT-3.5 models for contract analysis',
      models: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo'],
      recommended: false,
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      description: 'Claude models optimized for legal document understanding',
      models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
      recommended: true,
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Gemini Pro for multi-modal contract analysis',
      models: ['gemini-pro', 'gemini-pro-vision'],
      recommended: false,
    },
  ];

  const handleSave = async () => {
    try {
      // Save Slack webhooks if any are configured
      if (Object.values(slackWebhooks).some(url => url.trim() !== '')) {
        await notificationAPI.saveSlackWebhooks(slackWebhooks);
      }

      // TODO: Save LLM provider settings to backend
      console.log('Saving settings:', { selectedProvider, apiKeys, models });

      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Configure LLM providers and models for AI-powered contract intelligence
        </p>
      </div>

      {/* LLM Provider Selection */}
      <Card>
        <CardHeader>
          <CardTitle>LLM Provider</CardTitle>
          <CardDescription>
            Choose your preferred large language model provider for contract analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className={`flex items-start justify-between rounded-lg border-2 p-4 cursor-pointer transition-all ${
                selectedProvider === provider.id
                  ? 'border-gray-400 bg-gray-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedProvider(provider.id)}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{provider.name}</h3>
                  {provider.recommended && (
                    <Badge variant="default">Recommended</Badge>
                  )}
                  {selectedProvider === provider.id && (
                    <Check className="h-5 w-5 text-gray-700" />
                  )}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {provider.description}
                </p>
                <div className="mt-2">
                  <label className="text-xs font-medium text-muted-foreground">
                    Model:
                  </label>
                  <select
                    className="ml-2 text-sm border rounded px-2 py-1"
                    value={models[provider.id as keyof typeof models]}
                    onChange={(e) =>
                      setModels({ ...models, [provider.id]: e.target.value })
                    }
                    onClick={(e) => e.stopPropagation()}
                  >
                    {provider.models.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* API Key Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
          <CardDescription>
            Securely store your API keys for LLM providers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {providers.map((provider) => (
            <div key={provider.id}>
              <label className="block text-sm font-medium mb-2">
                {provider.name} API Key
              </label>
              <input
                type="password"
                placeholder={`Enter your ${provider.name} API key`}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={apiKeys[provider.id as keyof typeof apiKeys]}
                onChange={(e) =>
                  setApiKeys({ ...apiKeys, [provider.id]: e.target.value })
                }
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* RAG Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>RAG Pipeline Configuration</CardTitle>
          <CardDescription>
            Configure vector database and retrieval settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Chunk Size
            </label>
            <input
              type="number"
              placeholder="1000"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              defaultValue={1000}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Number of characters per document chunk for vector embedding
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Chunk Overlap
            </label>
            <input
              type="number"
              placeholder="200"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              defaultValue={200}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Overlap between chunks to maintain context
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Top K Results
            </label>
            <input
              type="number"
              placeholder="5"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              defaultValue={5}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Number of relevant chunks to retrieve for context
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Vector Database
            </label>
            <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="qdrant">Qdrant (Connected)</option>
              <option value="pinecone">Pinecone</option>
              <option value="weaviate">Weaviate</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Slack Integration */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Send className="h-5 w-5" />
                Slack Integration
              </CardTitle>
              <CardDescription>
                Configure Slack webhooks for automated contract intelligence notifications
              </CardDescription>
            </div>
            <Badge variant="outline">Optional</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Risk Alerts Webhook */}
          <div className="space-y-2">
            <Label htmlFor="slack-risk">High-Risk Contract Alerts</Label>
            <Input
              id="slack-risk"
              type="url"
              placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
              value={slackWebhooks.riskAlerts}
              onChange={(e) => setSlackWebhooks({ ...slackWebhooks, riskAlerts: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Sends alerts when contracts with risk score ≥ 7.0 are detected (#legal-alerts channel recommended)
            </p>
          </div>

          {/* Policy Violations Webhook */}
          <div className="space-y-2">
            <Label htmlFor="slack-policy">Policy Violation Notifications</Label>
            <Input
              id="slack-policy"
              type="url"
              placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
              value={slackWebhooks.policyViolations}
              onChange={(e) => setSlackWebhooks({ ...slackWebhooks, policyViolations: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Notifies when policy violations are detected (#compliance channel recommended)
            </p>
          </div>

          {/* Contract Intake Webhook */}
          <div className="space-y-2">
            <Label htmlFor="slack-intake">Contract Upload Notifications</Label>
            <Input
              id="slack-intake"
              type="url"
              placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
              value={slackWebhooks.contractIntake}
              onChange={(e) => setSlackWebhooks({ ...slackWebhooks, contractIntake: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Notifies team when new contracts are uploaded (#contract-intake channel recommended)
            </p>
          </div>

          {/* Weekly Reports Webhook */}
          <div className="space-y-2">
            <Label htmlFor="slack-weekly">Weekly Contract Insights</Label>
            <Input
              id="slack-weekly"
              type="url"
              placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
              value={slackWebhooks.weeklyReports}
              onChange={(e) => setSlackWebhooks({ ...slackWebhooks, weeklyReports: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Sends weekly contract intelligence summary (#executive-summary channel recommended)
            </p>
          </div>

          {/* Setup Instructions */}
          <div className="rounded-lg bg-slate-100 p-4 text-sm">
            <p className="font-semibold mb-2">How to get Slack webhook URLs:</p>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
              <li>Go to your Slack workspace settings</li>
              <li>Navigate to Apps → Incoming Webhooks</li>
              <li>Click "Add to Slack" and select a channel</li>
              <li>Copy the webhook URL and paste it above</li>
              <li>Repeat for each notification type you want to enable</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} className="gap-2">
          {saved ? (
            <>
              <Check className="h-4 w-4" />
              Saved!
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
