/**
 * API client configuration with interceptors.
 * Provides authenticated requests with automatic token injection.
 */
/* eslint-disable @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-argument */

//const API_URL = import.meta.env['VITE_API_URL'] || 'https://ytsummarizer.railway.internal';
const API_URL = 'https://ytsummarizer.railway.internal';

export type ApiResponse<T> = {
  data: T;
  status: number;
};

export type ApiError = {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
};

function toErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') {
    return fallback;
  }

  const errorPayload = payload as {
    detail?: unknown;
    message?: unknown;
    error_code?: unknown;
  };

  if (typeof errorPayload.message === 'string' && errorPayload.message.trim()) {
    return errorPayload.message;
  }

  if (typeof errorPayload.detail === 'string' && errorPayload.detail.trim()) {
    return errorPayload.detail;
  }

  if (
    errorPayload.detail &&
    typeof errorPayload.detail === 'object' &&
    'message' in errorPayload.detail &&
    typeof (errorPayload.detail as { message?: unknown }).message === 'string'
  ) {
    const nestedMessage = (errorPayload.detail as { message: string }).message.trim();
    if (nestedMessage) {
      return nestedMessage;
    }
  }

  return fallback;
}

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('access_token');
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');

    const token = this.getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (!response.ok) {
      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      const message = toErrorMessage(payload, `Request failed (${response.status})`);
      throw new Error(message);
    }

    const data = await response.json();
    return { data, status: response.status };
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    const options: RequestInit = { method: 'POST' };
    if (body !== undefined) {
      options.body = JSON.stringify(body);
    }

    return this.request<T>(endpoint, options);
  }

  async put<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    const options: RequestInit = { method: 'PUT' };
    if (body !== undefined) {
      options.body = JSON.stringify(body);
    }

    return this.request<T>(endpoint, options);
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(API_URL);
