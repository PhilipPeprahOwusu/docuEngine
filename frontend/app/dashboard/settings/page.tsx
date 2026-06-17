'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Save, Check, Send, Copy, Eye, EyeOff, Trash2, AlertTriangle, Key, RefreshCw } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { notificationAPI, settingsAPI } from '@/lib/api';

interface SavedAPIKey {
  provider: string;
  key_preview: string;
  model_name: string;
  created_at?: string;
  updated_at?: string;
}

export default function SettingsPage() {
  const [selectedProvider, setSelectedProvider] = useState('anthropic');
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({
    openai: '',
    anthropic: '',
    gemini: '',
  });
  const [savedKeys, setSavedKeys] = useState<SavedAPIKey[]>([]);
  const [models, setModels] = useState({
    openai: 'gpt-4o',
    anthropic: 'claude-3-5-sonnet-20240620',
    gemini: 'gemini-1.5-pro',
  });
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({});
  const [fetchingModels, setFetchingModels] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{provider: string; success: boolean; message: string} | null>(null);
  const [slackWebhooks, setSlackWebhooks] = useState({
    riskAlerts: '',
    policyViolations: '',
    contractIntake: '',
    weeklyReports: '',
  });
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  // Modal states
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [newApiKey, setNewApiKey] = useState<{
    provider: string;
    api_key: string;
    key_preview: string;
    model_name: string;
  } | null>(null);
  const [copied, setCopied] = useState(false);
  const [confirmExit, setConfirmExit] = useState(false);

  // Delete confirmation
  const [deleteProvider, setDeleteProvider] = useState<string | null>(null);

  // Regenerate confirmation
  const [regenerateProvider, setRegenerateProvider] = useState<string | null>(null);

  const providers = [
    {
      id: 'openai',
      name: 'OpenAI',
      description: 'GPT-4, GPT-3.5 models for contract analysis',
      recommended: false,
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      description: 'Claude models optimized for legal document understanding',
      recommended: true,
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Gemini Pro for multi-modal contract analysis',
      recommended: false,
    },
  ];

  useEffect(() => {
    loadSavedKeys();
    // Don't load hardcoded models - only show models after dynamic fetch with API key
  }, []);

  const loadAvailableModels = async () => {
    try {
      const response = await settingsAPI.getModels();
      setAvailableModels(response.data.models);
    } catch (error) {
      console.error('Failed to load available models:', error);
    }
  };

  const loadSavedKeys = async () => {
    try {
      const response = await settingsAPI.getAPIKeys();
      setSavedKeys(response.data.api_keys);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const handleFetchModels = async () => {
    const provider = selectedProvider;
    const apiKey = apiKeys[provider as keyof typeof apiKeys];
    const modelName = models[provider as keyof typeof models];

    if (!apiKey || apiKey.trim() === '') {
      setTestResult({
        provider,
        success: false,
        message: 'Please enter an API key first'
      });
      return;
    }

    setFetchingModels(true);
    setTestResult(null);

    try {
      const response = await settingsAPI.listAvailableModels(provider, apiKey, modelName);

      if (response.data.success && response.data.models.length > 0) {
        // Update available models for this provider
        setAvailableModels({
          ...availableModels,
          [provider]: response.data.models
        });

        // Set the first model as default
        setModels({
          ...models,
          [provider]: response.data.models[0]
        });

        setTestResult({
          provider,
          success: true,
          message: `Found ${response.data.models.length} available model(s) for your API key`
        });
      } else {
        // Clear available models for this provider when none are accessible
        setAvailableModels({
          ...availableModels,
          [provider]: []
        });

        setTestResult({
          provider,
          success: false,
          message: response.data.message || 'No models found for this API key'
        });
      }
    } catch (error: any) {
      // Clear available models on error
      setAvailableModels({
        ...availableModels,
        [provider]: []
      });

      setTestResult({
        provider,
        success: false,
        message: error.response?.data?.message || 'Failed to fetch models'
      });
    } finally {
      setFetchingModels(false);
    }
  };

  const handleTestConnection = async () => {
    const provider = selectedProvider;
    const apiKey = apiKeys[provider as keyof typeof apiKeys];
    const modelName = models[provider as keyof typeof models];

    if (!apiKey || apiKey.trim() === '') {
      setTestResult({
        provider,
        success: false,
        message: 'Please enter an API key first'
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await settingsAPI.testAPIKey(provider, apiKey, modelName);
      setTestResult({
        provider,
        success: response.data.success,
        message: response.data.message
      });
    } catch (error: any) {
      setTestResult({
        provider,
        success: false,
        message: error.response?.data?.message || 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const getSavedKey = (provider: string): SavedAPIKey | undefined => {
    return savedKeys.find(k => k.provider === provider);
  };

  const handleSaveAPIKey = async () => {
    const provider = selectedProvider;
    const apiKey = apiKeys[provider as keyof typeof apiKeys];
    const modelName = models[provider as keyof typeof models];

    if (!apiKey || apiKey.trim() === '') {
      alert('Please enter an API key');
      return;
    }

    setSaving(true);
    try {
      const response = await settingsAPI.saveAPIKey(provider, apiKey, modelName);

      // Show the full API key ONE TIME in modal
      setNewApiKey({
        provider: response.data.provider,
        api_key: response.data.api_key,
        key_preview: response.data.key_preview,
        model_name: response.data.model_name,
      });
      setShowKeyModal(true);

      // Clear the input
      setApiKeys({ ...apiKeys, [provider]: '' });

      // Reload saved keys to show the masked version
      await loadSavedKeys();

    } catch (error: any) {
      console.error('Failed to save API key:', error);
      alert(error.response?.data?.detail || 'Failed to save API key');
    } finally {
      setSaving(false);
    }
  };

  const handleCopyKey = () => {
    if (newApiKey) {
      navigator.clipboard.writeText(newApiKey.api_key);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCloseModal = () => {
    if (!copied) {
      setConfirmExit(true);
    } else {
      setShowKeyModal(false);
      setNewApiKey(null);
    }
  };

  const forceCloseModal = () => {
    setShowKeyModal(false);
    setNewApiKey(null);
    setConfirmExit(false);
  };

  const handleDeleteKey = async (provider: string) => {
    try {
      await settingsAPI.deleteAPIKey(provider);
      await loadSavedKeys();
      setDeleteProvider(null);
    } catch (error) {
      console.error('Failed to delete API key:', error);
      alert('Failed to delete API key');
    }
  };

  const handleRegenerateKey = (provider: string) => {
    setSelectedProvider(provider);
    setRegenerateProvider(provider);
  };

  const confirmRegenerate = () => {
    setRegenerateProvider(null);
    // The provider is already selected, user just needs to enter new key
  };

  const handleSlackSave = async () => {
    try {
      if (Object.values(slackWebhooks).some(url => url.trim() !== '')) {
        await notificationAPI.saveSlackWebhooks(slackWebhooks);
      }

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

      {/* LLM Provider & Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            LLM Provider Configuration
          </CardTitle>
          <CardDescription>
            Choose your preferred AI provider and configure API credentials
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Provider Selection */}
          <div className="space-y-3">
            <label className="block text-sm font-medium">
              Select LLM Provider
            </label>
            <div className="grid gap-3">
              {providers.map((provider) => {
                const savedKey = getSavedKey(provider.id);

                return (
                  <div
                    key={provider.id}
                    className={`flex items-center justify-between rounded-lg border-2 p-4 cursor-pointer transition-all ${
                      selectedProvider === provider.id
                        ? 'border-gray-900 bg-gray-50 shadow-sm'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedProvider(provider.id)}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        selectedProvider === provider.id
                          ? 'border-gray-900 bg-gray-900'
                          : 'border-gray-300'
                      }`}>
                        {selectedProvider === provider.id && (
                          <div className="w-2 h-2 rounded-full bg-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{provider.name}</h3>
                          {provider.recommended && (
                            <Badge variant="default" className="text-xs">Recommended</Badge>
                          )}
                          {savedKey && (
                            <Badge variant="outline" className="text-xs text-green-600 border-green-600">
                              <Check className="h-3 w-3 mr-1" />
                              Configured
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-0.5">
                          {provider.description}
                        </p>
                        {savedKey && (
                          <div className="mt-2 flex items-center gap-2">
                            <span className="text-xs text-muted-foreground font-mono">
                              API Key: {savedKey.key_preview}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              • Model: {savedKey.model_name}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    {savedKey && (
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRegenerateKey(provider.id);
                          }}
                        >
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Regenerate
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteProvider(provider.id);
                          }}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Provider Configuration */}
          {selectedProvider && (
            <div className="space-y-4 pt-4 border-t">
              {(() => {
                const provider = providers.find(p => p.id === selectedProvider);
                if (!provider) return null;

                const savedKey = getSavedKey(provider.id);

                return (
                  <>
                    <div className="flex items-center gap-2 mb-4">
                      <Check className="h-5 w-5 text-green-600" />
                      <span className="font-medium">
                        {savedKey ? `Update ${provider.name}` : `Configure ${provider.name}`}
                      </span>
                    </div>

                    {savedKey && (
                      <Alert className="bg-blue-50 border-blue-200">
                        <AlertTriangle className="h-4 w-4 text-blue-600" />
                        <AlertDescription className="text-sm text-blue-800">
                          You already have an API key configured. Entering a new key will replace the existing one.
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* API Key Input */}
                    <div className="space-y-2">
                      <Label htmlFor="api-key" className="text-sm font-medium">
                        {provider.name} API Key
                      </Label>
                      <Input
                        id="api-key"
                        type="password"
                        placeholder={`Enter your ${provider.name} API key`}
                        value={apiKeys[provider.id as keyof typeof apiKeys]}
                        onChange={(e) =>
                          setApiKeys({ ...apiKeys, [provider.id]: e.target.value })
                        }
                        className="font-mono text-sm"
                      />
                      <p className="text-xs text-muted-foreground">
                        Your API key is encrypted and stored securely. You'll only see it once after saving.
                      </p>
                    </div>

                    {/* Fetch Available Models Button */}
                    <div className="space-y-2">
                      <Button
                        onClick={handleFetchModels}
                        disabled={fetchingModels || !apiKeys[provider.id as keyof typeof apiKeys]?.trim()}
                        variant="outline"
                        className="w-full"
                        type="button"
                      >
                        {fetchingModels ? (
                          <>
                            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            Fetching Available Models...
                          </>
                        ) : (
                          <>
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Fetch Available Models
                          </>
                        )}
                      </Button>
                      <p className="text-xs text-muted-foreground">
                        Detect which models your API key has access to
                      </p>
                    </div>

                    {/* Model Selection */}
                    {availableModels[provider.id] && availableModels[provider.id].length > 0 && (
                      <div className="space-y-2">
                        <Label htmlFor="model-select" className="text-sm font-medium">
                          Select Model
                        </Label>
                        <select
                          id="model-select"
                          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
                          value={models[provider.id as keyof typeof models]}
                          onChange={(e) =>
                            setModels({ ...models, [provider.id]: e.target.value })
                          }
                        >
                          {availableModels[provider.id].map((model) => (
                            <option key={model} value={model}>
                              {model}
                            </option>
                          ))}
                        </select>
                        <p className="text-xs text-muted-foreground">
                          {availableModels[provider.id].length} model(s) available with your API key
                        </p>
                      </div>
                    )}

                    {/* Test Connection */}
                    {testResult && testResult.provider === provider.id && (
                      <Alert variant={testResult.success ? "default" : "destructive"} className="text-sm">
                        <AlertDescription>
                          {testResult.success ? '✓ ' : '✗ '}
                          {testResult.message}
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Action Buttons - Only show when models are fetched */}
                    {availableModels[provider.id] && availableModels[provider.id].length > 0 && (
                      <div className="flex gap-2">
                        <Button
                          onClick={handleTestConnection}
                          disabled={testing || !apiKeys[provider.id as keyof typeof apiKeys]?.trim()}
                          variant="outline"
                          className="flex-1"
                        >
                          {testing ? (
                            <>
                              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                              Testing...
                            </>
                          ) : (
                            <>
                              <Send className="mr-2 h-4 w-4" />
                              Test Model
                            </>
                          )}
                        </Button>
                        <Button
                          onClick={handleSaveAPIKey}
                          disabled={saving || !apiKeys[provider.id as keyof typeof apiKeys]?.trim()}
                          className="flex-1"
                        >
                          {saving ? (
                            <>
                              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              <Save className="mr-2 h-4 w-4" />
                              {savedKey ? 'Update' : 'Save'}
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          )}
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
              Sends alerts when contracts with risk score ≥ 7.0 are detected
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
              Notifies when policy violations are detected
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
              Notifies team when new contracts are uploaded
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
              Sends weekly contract intelligence summary
            </p>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSlackSave} variant="outline" className="gap-2">
              {saved ? (
                <>
                  <Check className="h-4 w-4" />
                  Saved!
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Slack Settings
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Show Once Modal */}
      <Dialog open={showKeyModal} onOpenChange={() => handleCloseModal()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Save Your API Key
            </DialogTitle>
            <DialogDescription>
              This is the <strong>only time</strong> you'll see this API key. Make sure to copy it now!
            </DialogDescription>
          </DialogHeader>

          {newApiKey && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Provider</Label>
                <div className="text-sm font-medium capitalize">{newApiKey.provider}</div>
              </div>

              <div className="space-y-2">
                <Label>API Key</Label>
                <div className="flex items-center gap-2">
                  <Input
                    value={newApiKey.api_key}
                    readOnly
                    className="font-mono text-xs"
                  />
                  <Button
                    size="sm"
                    onClick={handleCopyKey}
                    variant={copied ? "default" : "outline"}
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4 mr-1" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <Alert className="bg-orange-50 border-orange-200">
                <AlertTriangle className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-sm text-orange-800">
                  After closing this dialog, the key will be masked and cannot be retrieved again.
                  You'll need to regenerate it if you lose it.
                </AlertDescription>
              </Alert>
            </div>
          )}

          <DialogFooter>
            <Button
              onClick={forceCloseModal}
              disabled={!copied}
              className="w-full"
            >
              {copied ? "I've Saved My Key" : 'Copy Key First'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirm Exit Dialog */}
      <AlertDialog open={confirmExit} onOpenChange={setConfirmExit}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              You haven't copied your API key yet. If you close this dialog without copying,
              you won't be able to see the full key again.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Go Back</AlertDialogCancel>
            <AlertDialogAction onClick={forceCloseModal}>
              Close Anyway
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Confirmation */}
      <AlertDialog open={deleteProvider !== null} onOpenChange={() => setDeleteProvider(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete API Key?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the {deleteProvider?.toUpperCase()} API key.
              You'll need to enter a new one to use this provider.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteProvider && handleDeleteKey(deleteProvider)}
              className="bg-destructive text-destructive-foreground"
            >
              Delete Key
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Regenerate Confirmation */}
      <AlertDialog open={regenerateProvider !== null} onOpenChange={() => setRegenerateProvider(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Regenerate API Key?</AlertDialogTitle>
            <AlertDialogDescription>
              This will replace your existing {regenerateProvider?.toUpperCase()} API key with a new one.
              Enter the new key below to continue.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmRegenerate}>
              Continue
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
