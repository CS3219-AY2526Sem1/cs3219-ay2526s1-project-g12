import { Link } from 'react-router';
import React, { useState } from 'react';
import { userApi } from '../../api/UserApi.tsx';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    if (!email) {
      setError('Please enter your email.');
      setSubmitting(false);
      return;
    }

    const response = await userApi.forgotPassword(email);

    if (response.error) {
      setError('Please enter a valid email.');
      setSubmitting(false);
      return;
    } else {
      setSuccess(true);
      setError(null);
      setEmail('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex flex-col justify-center max-w-md w-full min-h-screen mx-auto space-y-4">
        <h2 className="font-medium">Forgot Password</h2>

        {success && (
          <div className="alert alert-success alert-soft mb-6">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 shrink-0 stroke-current"
              fill="none"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>
              Success! If an account exists with that email, a password reset
              link has been sent.
            </span>
          </div>
        )}

        {error && (
          <div className="alert alert-error alert-soft">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 shrink-0 stroke-current"
              fill="none"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
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
        </fieldset>

        <button
          type="submit"
          disabled={submitting}
          className="btn btn-primary w-full font-normal"
        >
          {submitting ? (
            success ? (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 shrink-0 stroke-current"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Success
              </>
            ) : (
              <>
                <span className="loading loading-spinner loading-sm mr-2"></span>
                Submitting...
              </>
            )
          ) : (
            'Submit'
          )}
        </button>

        {/* Login Link at Bottom */}
        <p className="text-center">
          <Link to="/auth/login" className="underline">
            Back to login
          </Link>
        </p>
      </div>
    </form>
  );
}
