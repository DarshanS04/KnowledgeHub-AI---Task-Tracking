import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserResponse, LoginRequest, SignupRequest } from '../types';
import { authApi } from '../api/auth';
import { apiClient } from '../api/client';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (credentials: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from local storage on startup
  useEffect(() => {
    const initializeAuth = () => {
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('access_token');

      if (storedUser && token) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          // Corrupted user data, wipe auth
          localStorage.removeItem('user');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setIsLoading(false);
    };

    initializeAuth();

    // Listen for custom logout events from Axios client (e.g. on 401 refresh failure)
    const handleSessionExpired = () => {
      setUser(null);
    };

    window.addEventListener('auth_session_expired', handleSessionExpired);
    return () => {
      window.removeEventListener('auth_session_expired', handleSessionExpired);
    };
  }, []);

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      const data = await authApi.login(credentials);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      setUser(data.user);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (credentials: SignupRequest) => {
    setIsLoading(true);
    try {
      await authApi.signup(credentials);
      // Auto login after signup
      await login({ email: credentials.email, password: credentials.password });
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch (e) {
      console.error('Logout API call failed, removing local credentials anyway', e);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      delete apiClient.defaults.headers.common['Authorization'];
      setUser(null);
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
