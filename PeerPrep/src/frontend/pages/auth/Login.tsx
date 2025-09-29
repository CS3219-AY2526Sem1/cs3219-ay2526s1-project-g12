import React, { useState, useEffect } from 'react';
import { apiClient } from '../../components/api';
import GitHubLogo from '../../assets/Images/github-logo.png';
import GoogleLogo from '../../assets/Images/google-logo.png';
import { Link } from 'react-router';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role_id: number;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Check if user is already authenticated on component mount
  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const userRes = await apiClient.getCurrentUser();
        if (userRes.data && !userRes.error) {
          setUser(userRes.data as User);
        }
      } catch (err) {
        console.log('User not authenticated');
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuthentication();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    console.log('Login attempt:', email);

    try {
      const loginRes = await apiClient.login(email, password);

      if (loginRes.error) {
        setError(loginRes.error);
      } else { // Login successful - FastAPI-Users typically returns 204 No Content
        // fetch the current user to confirm authentication
        const userRes = await apiClient.getCurrentUser();

        if (userRes.data && !userRes.error) {
          setUser(userRes.data as User);
          setEmail(''); // Clear form
          setPassword('');
        } else {
          setError('Login succeeded but failed to fetch user data');
        }
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Unexpected error during login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setEmail('');
      setPassword('');
      setError(null);
    } catch (err) {
      console.error('Logout error:', err);
      setError('Failed to logout');
    }
  };

  // Show loading spinner while checking authentication
  if (checkingAuth) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  // User is authenticated - show welcome screen
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Welcome back!
            </h2>
            <div className="mt-4 p-6 bg-white rounded-lg shadow-md">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {user.first_name} {user.last_name}
              </h3>
              <p className="text-gray-600 mb-2">
                <strong>Email:</strong> {user.email}
              </p>
              <p className="text-gray-600 mb-2">
                <strong>Status:</strong> {user.is_active ? 'Active' : 'Inactive'}
              </p>
              <p className="text-gray-600 mb-4">
                <strong>Verified:</strong> {user.is_verified ? 'Yes' : 'No'}
              </p>

              <button
                onClick={handleLogout}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // User is not authenticated - show login form
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign In
          </h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          {error && (
            <div className="alert alert-error">
              <span>{error}</span>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div className="mb-4">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input input-bordered w-full"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="input input-bordered w-full"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <span className="loading loading-spinner loading-sm mr-2"></span>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">OR</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                disabled
              >
                <img className="h-5 w-5" src={GoogleLogo} alt="Google logo" />
                <span className="ml-2">Google</span>
              </button>

              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                disabled
              >
                <img className="h-5 w-5" src={GitHubLogo} alt="GitHub logo" />
                <span className="ml-2">GitHub</span>
              </button>
            </div>
          </div>
          {/* Additional Register Link at Bottom */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              New to our platform?{' '}
              <Link
                to="/auth/register"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Sign up for free
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}