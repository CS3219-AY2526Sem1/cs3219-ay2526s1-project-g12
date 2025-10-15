import React, { useState, useEffect } from "react";
import { apiClient } from "../../components/api";
import GitHubLogo from "../../assets/Images/github-logo.png";
import GoogleLogo from "../../assets/Images/google-logo.png";
import { Link } from "react-router";

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
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
          setUser(userRes.data.user_data as User);
        }
      } catch (err) {
        console.log("User not authenticated");
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

    console.log("Login attempt:", email);

    try {
      const loginRes = await apiClient.login(email, password);

      if (loginRes.error) {
        console.error("Login failed:", loginRes.error);
        setError(loginRes.error.detail || "Login failed");
      } else {
        // Login successful - FastAPI-Users typically returns 204 No Content
        // fetch the current user to confirm authentication
        const userRes = await apiClient.getCurrentUser();
        console.log("Fetched user data:", userRes);

        if (userRes.data && !userRes.error) {
          setUser(userRes.data.user_data as User);
          // Route to new page
          setEmail(""); // Clear form
          setPassword("");
        } else {
          setError("Login succeeded but failed to fetch user data");
        }
      }
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.message || "Unexpected error during login");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setEmail("");
      setPassword("");
      setError(null);
    } catch (err) {
      console.error("Logout error:", err);
      setError("Failed to logout");
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

  // User is authenticated - show welcome screen [to be replaced with dashboard]
  if (user) {
    console.log("User is authenticated:", user);
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
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
                <strong>Status:</strong>{" "}
                {user.is_active ? "Active" : "Inactive"}
              </p>
              <p className="text-gray-600 mb-4">
                <strong>Verified:</strong> {user.is_verified ? "Yes" : "No"}
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
    <form onSubmit={handleLogin}>
      <div className="flex flex-col justify-center max-w-md w-full min-h-screen mx-auto space-y-4">
        <div>
          <span className="text-[clamp(0.85rem,0.8vw,1rem)] font-medium tracking-[0.20em]">
            WELCOME BACK TO
          </span>
          <br />
          <span className="peerprep-logo">PeerPrep</span>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
        )}

        <fieldset className="pb-3">
          <label htmlFor="email" className="fieldset-legend font-normal">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="input validator w-full"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />

          <label htmlFor="password" className="fieldset-legend font-normal">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className="input validator w-full"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />

          <Link to="/auth/reset" className="font-light text-sm underline">
            Forgot your password?
          </Link>
        </fieldset>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-full font-normal"
        >
          {loading ? (
            <>
              <span className="loading loading-spinner loading-sm mr-2"></span>
              Signing in...
            </>
          ) : (
            "Sign In"
          )}
        </button>

        <div className="divider divider-neutral mt-0">OR</div>

        {/* UI to sign in using other platforms */}
        {/* Hides Google login btn for now*/}
        {/*
         <button
          type="button"
          className="btn btn-primary btn-soft w-full font-normal pb-3"
          disabled
        >
          <img className="h-5 w-5" src={GoogleLogo} alt="Google logo" />
          <span className="ml-2">Continue with Google</span>
        </button> 
        */}

        <button
          type="button"
          className="btn btn-primary btn-soft w-full font-normal mb-3"
          disabled // Disable until Github login is set up
        >
          <img className="h-5 w-5" src={GitHubLogo} alt="GitHub logo" />
          <span className="ml-2">Continue with GitHub</span>
        </button>

        {/* Additional Register Link at Bottom */}
        <p className="text-center">
          Don't have an account?&nbsp;
          <Link to="/auth/register" className="underline">
            Sign up
          </Link>
        </p>
      </div>
    </form>
  );
}
