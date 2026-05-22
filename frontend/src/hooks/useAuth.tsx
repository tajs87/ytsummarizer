/**
 * Authentication context and hooks for managing user authentication state.
 * Provides login, register, logout, and current user management.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/api';

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token and load user on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = apiClient.getToken();
      if (token) {
        try {
          const response = await apiClient.get<User>('/api/v1/auth/me');
          setUser(response.data);
        } catch (error) {
          // Token invalid or expired, clear it
          apiClient.clearToken();
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${import.meta.env['VITE_API_URL'] || 'http://localhost:8000'}/api/v1/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    apiClient.setToken(data.access_token);

    // Fetch user details
    const userResponse = await apiClient.get<User>('/api/v1/auth/me');
    setUser(userResponse.data);
  };

  const register = async (email: string, password: string) => {
    const response = await apiClient.post<{ access_token: string }>('/api/v1/auth/register', {
      email,
      password,
    });

    apiClient.setToken(response.data.access_token);

    // Fetch user details
    const userResponse = await apiClient.get<User>('/api/v1/auth/me');
    setUser(userResponse.data);
  };

  const logout = () => {
    apiClient.clearToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
