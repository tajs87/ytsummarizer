/**
 * API client configuration with interceptors.
 * Provides authenticated requests with automatic token injection.
 */

const API_URL = import.meta.env['VITE_API_URL'] || 'http://localhost:8000';

export type ApiResponse<T> = {
  data: T;
  status: number;
};

export type ApiError = {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
};

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

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
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
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw error;
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
