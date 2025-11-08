import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { userApi } from '../api/UserApi';
import type { User } from '../types/User.tsx';
import { useLocation } from 'react-router-dom';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => Promise<boolean>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const location = useLocation();

  // Load user on mount (if logged in)
  useEffect(() => {
    const fetchUser = async () => {
      const { data, error } = await userApi.getCurrentUser();
      if (data) setUser(data);
      else if (error) console.warn('User not authenticated:', error);
      setIsLoading(false);
    };
    fetchUser();
  }, []);

  // clear error whenever route changes
  useEffect(() => {
    setError(null);
  }, [location.pathname]);

  const login = async (email: string, password: string) => {
    const { error } = await userApi.login(email, password);
    if (error) {
      setError(error);
      return false;
    }

    const { data } = await userApi.getCurrentUser();
    if (data) {
      setUser(data);
      return true;
    }
    return false;
  };

  const register = async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => {
    const { data, error } = await userApi.register(userData);
    if (data) {
      setUser(data);
      return true;
    }
    if (error) {
      setError(error);
    }
    return false;
  };

  const logout = async () => {
    await userApi.logout();
    setUser(null);
    setError(null);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, error, login, logout, register, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
