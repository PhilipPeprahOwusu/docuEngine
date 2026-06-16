'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Save, Check } from 'lucide-react';

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

  const handleSave = () => {
    // In real app, save to backend
    console.log('Saving settings:', { selectedProvider, apiKeys, models });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
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
