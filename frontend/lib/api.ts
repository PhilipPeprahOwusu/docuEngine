import axios from 'axios';

// Backend API URL
// In production (Vercel), use empty string to use the proxy route at /api/*
// In development, use direct backend URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_USE_PROXY === 'true'
  ? '' // Use relative URLs to hit the Vercel proxy
  : (process.env.NEXT_PUBLIC_API_URL || 'http://136.116.180.162');

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  // Don't set default Content-Type - let axios auto-detect based on request body
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  register: (data: { email: string; password: string; username: string }) =>
    api.post('/api/v1/auth/register', data),

  login: (username: string, password: string) =>
    api.post('/api/v1/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  refreshToken: (refreshToken: string) =>
    api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
};

export const userAPI = {
  getMe: () => api.get('/api/v1/users/me'),
  getUsers: () => api.get('/api/v1/users/'),
  updateUser: (userId: string, data: any) => api.put(`/api/v1/users/${userId}`, data),
};

export const documentAPI = {
  upload: (formData: FormData) =>
    api.post('/api/v1/documents/upload', formData),

  list: () => api.get('/api/v1/documents/'),
  get: (documentId: string) => api.get(`/api/v1/documents/${documentId}`),
  delete: (documentId: string) => api.delete(`/api/v1/documents/${documentId}`),
};

export const agentAPI = {
  // Built-in agent execution
  extract: (documentId: string) => api.post(`/api/v1/agents/extract/${documentId}`),
  risk: (documentId: string) => api.post(`/api/v1/agents/risk/${documentId}`),
  compare: (documentAId: string, documentBId: string) =>
    api.post('/api/v1/agents/compare', { document_a_id: documentAId, document_b_id: documentBId }),
  qa: (documentId: string, question: string) =>
    api.post(`/api/v1/agents/qa/${documentId}`, { question }),

  // Custom agent management
  listCustomAgents: () => api.get('/api/v1/agents/custom'),
  createCustomAgent: (data: {
    name: string;
    description: string;
    system_prompt: string;
    temperature?: number;
    max_tokens?: number;
    capabilities?: string[];
  }) => api.post('/api/v1/agents/custom', data),
  getCustomAgent: (agentId: string) => api.get(`/api/v1/agents/custom/${agentId}`),
  updateCustomAgent: (agentId: string, data: any) => api.put(`/api/v1/agents/custom/${agentId}`, data),
  deleteCustomAgent: (agentId: string) => api.delete(`/api/v1/agents/custom/${agentId}`),
  executeCustomAgent: (agentId: string, documentId: string, params?: any) =>
    api.post(`/api/v1/agents/custom/${agentId}/execute`, { document_id: documentId, ...params }),
};

export const policyAPI = {
  list: () => api.get('/api/v1/policies/'),
  create: (data: any) => api.post('/api/v1/policies/', data),
  update: (policyId: string, data: any) => api.put(`/api/v1/policies/${policyId}`, data),
  delete: (policyId: string) => api.delete(`/api/v1/policies/${policyId}`),
};

export const notificationAPI = {
  // Slack webhook configuration
  saveSlackWebhooks: (webhooks: {
    riskAlerts?: string;
    policyViolations?: string;
    contractIntake?: string;
    weeklyReports?: string;
  }) => api.post('/api/v1/notifications/slack/webhooks', webhooks),

  getSlackWebhooks: () => api.get('/api/v1/notifications/slack/webhooks'),

  // Trigger Slack notifications manually
  sendRiskAlert: (documentId: string, riskData: any) =>
    api.post('/api/v1/notifications/slack/risk-alert', { document_id: documentId, ...riskData }),

  sendPolicyViolation: (documentId: string, violations: any[]) =>
    api.post('/api/v1/notifications/slack/policy-violation', { document_id: documentId, violations }),

  sendContractIntake: (documentId: string) =>
    api.post('/api/v1/notifications/slack/contract-intake', { document_id: documentId }),

  // Test webhook
  testSlackWebhook: (webhookUrl: string) =>
    api.post('/api/v1/notifications/slack/test', { webhook_url: webhookUrl }),
};

export const approvalsAPI = {
  // Exception requests
  requestException: (data: {
    document_id: string;
    policy_id: string;
    violation_id: string;
    exception_reason: string;
    valid_until?: string;
  }) => api.post('/api/v1/approvals/exceptions/request', data),

  // Get exceptions (role-based views)
  getPendingExceptions: () => api.get('/api/v1/approvals/exceptions/pending'),
  getApprovedExceptions: () => api.get('/api/v1/approvals/exceptions/approved'),
  getRejectedExceptions: () => api.get('/api/v1/approvals/exceptions/rejected'),

  // Approve/reject exceptions (Approver-only)
  approveException: (exceptionId: string) =>
    api.post(`/api/v1/approvals/exceptions/${exceptionId}/approve`),

  rejectException: (exceptionId: string, rejectionReason?: string) =>
    api.post(`/api/v1/approvals/exceptions/${exceptionId}/reject`, {
      decision: 'reject',
      rejection_reason: rejectionReason
    }),

  // Finalize contract (Approver-only)
  finalizeContract: (documentId: string) =>
    api.post(`/api/v1/approvals/documents/${documentId}/finalize`),

  // Download finalized PDF
  getFinalizedPDF: (documentId: string) =>
    api.get(`/api/v1/approvals/documents/${documentId}/pdf`),
};
