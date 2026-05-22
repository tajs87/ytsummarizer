/**
 * Authentication context and hooks for managing user authentication state.
 * Provides login, register, logout, and current user management.
 */
/* eslint-disable react-refresh/only-export-components */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import type { AuthToken } from '@/types/api';

export type User = {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
};

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  migratedItems: number;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [migratedItems, setMigratedItems] = useState(0);
  const queryClient = useQueryClient();

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

    void loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post<AuthToken>('/api/v1/auth/login', {
      email,
      password,
    });

    apiClient.setToken(response.data.access_token);

    // Fetch user details
    const userResponse = await apiClient.get<User>('/api/v1/auth/me');
    setUser(userResponse.data);
    setMigratedItems(response.data.migrated_items ?? 0);
    await queryClient.invalidateQueries({ queryKey: ['videos'] });
  };

  const register = async (email: string, password: string) => {
    await apiClient.post('/api/v1/auth/register', {
      email,
      password,
    });

    // The register endpoint returns profile data, so log in after registration.
    await login(email, password);
  };

  const logout = () => {
    apiClient.clearToken();
    setUser(null);
    setMigratedItems(0);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        migratedItems,
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
