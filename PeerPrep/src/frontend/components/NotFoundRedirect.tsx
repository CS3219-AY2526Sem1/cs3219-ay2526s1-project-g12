import { Navigate } from 'react-router';
import { useAuth } from '../context/AuthContext';

export default function NotFoundRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  console.log('NotFoundRedirect:', user);
  // Redirect based on authentication status
  return user ? (
    <Navigate to="/dashboard" replace />
  ) : (
    <Navigate to="/" replace />
  );
}
