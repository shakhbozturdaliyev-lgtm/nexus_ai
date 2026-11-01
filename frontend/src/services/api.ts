const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/api` 
  : '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('nexus_auth_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('nexus_auth_token', token);
}

export function removeAuthToken(): void {
  localStorage.removeItem('nexus_auth_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeAuthToken();
    window.dispatchEvent(new Event('nexus_auth_invalid'));
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (credentials: { email: string; password: string }) =>
    request<{ access_token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  getMe: () => request<any>('/auth/me'),

  // Overview
  getOverviewMetrics: () => request<any>('/analytics/overview'),

  // Conversations
  listConversations: (status?: string, search?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    return request<{ count: number; items: any[] }>(`/conversations?${params.toString()}`);
  },
  getConversation: (id: number) => request<any>(`/conversations/${id}`),
  claimConversation: (id: number) =>
    request<any>(`/conversations/${id}/claim`, { method: 'POST' }),
  sendReply: (id: number, content: string) =>
    request<any>(`/conversations/${id}/reply`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),
  addNote: (id: number, content: string) =>
    request<any>(`/conversations/${id}/note`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),
  returnToAI: (id: number) =>
    request<any>(`/conversations/${id}/return_to_ai`, { method: 'POST' }),
  resolveConversation: (id: number, resolution_notes?: string) =>
    request<any>(`/conversations/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_notes }),
    }),

  // Products
  listProducts: (search?: string) => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    return request<{ count: number; items: any[] }>(`/products?${params.toString()}`);
  },
  createProduct: (data: any) =>
    request<any>('/products', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id: number, data: any) =>
    request<any>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deactivateProduct: (id: number) =>
    request<any>(`/products/${id}`, { method: 'DELETE' }),

  // Orders
  listOrders: (status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    return request<{ count: number; items: any[] }>(`/orders?${params.toString()}`);
  },
  updateOrderStatus: (id: number, status: string, notes?: string) =>
    request<any>(`/orders/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, notes }),
    }),

  // Tickets
  listTickets: (status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    return request<{ count: number; items: any[] }>(`/tickets?${params.toString()}`);
  },
  updateTicket: (id: number, data: any) =>
    request<any>(`/tickets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Knowledge Base
  listKnowledge: (category?: string, language?: string) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (language) params.append('language', language);
    return request<{ count: number; items: any[] }>(`/knowledge?${params.toString()}`);
  },
  createKnowledge: (data: any) =>
    request<any>('/knowledge', { method: 'POST', body: JSON.stringify(data) }),
  updateKnowledge: (id: number, data: any) =>
    request<any>(`/knowledge/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // AI Settings
  getAISettings: () => request<any>('/ai-settings'),
  updateAISettings: (data: any) =>
    request<any>('/ai-settings', { method: 'PUT', body: JSON.stringify(data) }),

  // Users
  listUsers: () => request<{ count: number; items: any[] }>('/users'),
  createUser: (data: any) =>
    request<any>('/users', { method: 'POST', body: JSON.stringify(data) }),

  // Business
  getBusiness: () => request<any>('/business'),
  updateBusiness: (data: any) =>
    request<any>('/business', { method: 'PUT', body: JSON.stringify(data) }),

  // Audit Logs
  listAuditLogs: () => request<{ count: number; items: any[] }>('/audit-logs'),
};
