import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { ReactElement } from 'react';

export const ProtectedRoute = ({ children }: { children: ReactElement }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!user || !user.is_verified) return <Navigate to="/auth/login" replace />;

  return children;
};
