import { Link, useSearchParams } from 'react-router';
import React, { useState } from 'react';
import { userApi } from '../../api/UserApi.tsx';

interface ResetForm {
  password: string;
  confirmPassword: string;
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [formData, setFormData] = useState<ResetForm>({
    password: '',
    confirmPassword: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordValidation, setPasswordValidation] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    numberOrSymbol: false,
  });

  // Password validation
  const validatePassword = (password: string) => {
    const validation = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      numberOrSymbol: /[\d\W_]/.test(password),
    };
    setPasswordValidation(validation);
    return Object.values(validation).every(Boolean);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Validate password in real-time
    if (name === 'password') {
      validatePassword(value);
    }

    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setSubmitting(false);
      return;
    }

    if (!validatePassword(formData.password)) {
      setError('Password does not meet requirements');
      setSubmitting(false);
      return;
    }

    const response = await userApi.resetPassword({
      token: token || '',
      password: formData.password,
    });

    if (response.error) {
      setError(response.error);
      setSubmitting(false);
      return;
    } else {
      setSuccess(true);
      setError(null);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex flex-col justify-center max-w-md w-full min-h-screen mx-auto space-y-4">
        <h2 className="font-medium">Reset Password</h2>

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
              Success! Your password has been reset. You may proceed to login
              now.
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
          <label htmlFor="password" className="fieldset-legend font-normal">
            New Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            className="input validator w-full"
            placeholder="Create a new password"
            value={formData.password}
            onChange={handleInputChange}
            disabled={submitting}
          />

          {/* Password Requirements */}
          {formData.password && (
            <div className="mt-2 text-xs space-y-1">
              <div
                className={`flex items-center ${passwordValidation.length ? 'text-success' : 'text-error'}`}
              >
                <span className="mr-1">
                  {passwordValidation.length ? '✓' : '✗'}
                </span>
                At least 8 characters
              </div>
              <div
                className={`flex items-center ${passwordValidation.uppercase ? 'text-success' : 'text-error'}`}
              >
                <span className="mr-1">
                  {passwordValidation.uppercase ? '✓' : '✗'}
                </span>
                One uppercase letter
              </div>
              <div
                className={`flex items-center ${passwordValidation.lowercase ? 'text-success' : 'text-error'}`}
              >
                <span className="mr-1">
                  {passwordValidation.lowercase ? '✓' : '✗'}
                </span>
                One lowercase letter
              </div>
              <div
                className={`flex items-center ${passwordValidation.numberOrSymbol ? 'text-success' : 'text-error'}`}
              >
                <span className="mr-1">
                  {passwordValidation.numberOrSymbol ? '✓' : '✗'}
                </span>
                One number or symbol
              </div>
            </div>
          )}

          {/* Confirm Password Field */}
          <label
            htmlFor="confirmPassword"
            className="fieldset-legend font-normal"
          >
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            autoComplete="new-password"
            required
            className={`input validator w-full ${
              formData.confirmPassword &&
              formData.password !== formData.confirmPassword
                ? 'border-error'
                : formData.confirmPassword &&
                    formData.password === formData.confirmPassword
                  ? 'border-success'
                  : ''
            }`}
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            disabled={submitting}
          />
          {formData.confirmPassword &&
            formData.password !== formData.confirmPassword && (
              <p className="mt-1 text-xs text-error">Passwords do not match</p>
            )}
        </fieldset>

        <button
          type="submit"
          disabled={
            submitting ||
            !Object.values(passwordValidation).every(Boolean) ||
            formData.password !== formData.confirmPassword
          }
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
