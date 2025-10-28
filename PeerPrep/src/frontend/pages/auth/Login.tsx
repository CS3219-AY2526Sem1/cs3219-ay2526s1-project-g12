import React, { useState, useEffect } from "react";
import GitHubLogo from "../../assets/Images/github-logo.png";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { user, login, error, clearError, isLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect authenticated user to dashboard
  useEffect(() => {
    if (user && user.is_verified) navigate("/dashboard");
  }, [user]);

  // Clear auth error when user starts typing again
  useEffect(() => {
    if (error) clearError();
  }, [email, password]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    console.log("Login attempt:", email);

    const success = await login(email, password);
    if (success) {
      setEmail("");
      setPassword("");
      navigate("/dashboard");
    }

    setSubmitting(false);
  };

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="loading loading-spinner loading-lg"></div>
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
            disabled={submitting}
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
            disabled={submitting}
          />

          <Link to="/auth/reset" className="font-light text-sm underline">
            Forgot your password?
          </Link>
        </fieldset>

        <button
          type="submit"
          disabled={submitting}
          className="btn btn-primary w-full font-normal"
        >
          {submitting ? (
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
