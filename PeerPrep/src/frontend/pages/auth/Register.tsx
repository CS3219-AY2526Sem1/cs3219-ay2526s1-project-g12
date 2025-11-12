import React, { useState } from 'react';
import { Link } from 'react-router';
import { useAuth } from '../../context/AuthContext';

interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
}

export default function Register() {
  const [formData, setFormData] = useState<RegisterForm>({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    numberOrSymbol: false,
  });
  const { user, register, error, clearError } = useAuth();

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
    if (validationError) setValidationError(null);
    if (error) clearError();
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    clearError();
    setValidationError(null);

    // Client-side validation
    if (
      !formData.email ||
      !formData.password ||
      !formData.first_name ||
      !formData.last_name
    ) {
      setValidationError('All fields are required');
      setSubmitting(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwords do not match');
      setSubmitting(false);
      return;
    }

    if (!validatePassword(formData.password)) {
      setValidationError('Password does not meet requirements');
      setSubmitting(false);
      return;
    }

    if (formData.email.includes(formData.password)) {
      setValidationError('Password should not contain your email address');
      setSubmitting(false);
      return;
    }

    console.log('Registration attempt:', formData.email);

    const success = await register({
      email: formData.email,
      password: formData.password,
      first_name: formData.first_name,
      last_name: formData.last_name,
    });

    if (success) {
      setSuccess(true);
      setFormData({
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
      });
    }

    setSubmitting(false);
  };

  // Success state - show registration confirmation
  if (success && user) {
    return (
      <div className="flex flex-col justify-center max-w-md w-full min-h-screen mx-auto space-y-4 text-center">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
          <svg
            className="h-6 w-6 text-success"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            ></path>
          </svg>
        </div>
        <h2 className="mt-6 text-3xl font-extrabold">
          Registration Successful!
        </h2>
        <div className="mt-4 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-medium mb-2">
            Welcome, {user.first_name} {user.last_name}!
          </h3>
          <p className="mb-2">
            <strong>Email:</strong> {user.email}
          </p>
          <p className="mb-4">
            <strong>Account Status:</strong>{' '}
            {user.is_verified ? 'Verified' : 'Pending Verification'}
          </p>

          <Link
            to="/auth/login" // route path
            className="btn btn-primary w-full font-normal"
          >
            Continue to Login
          </Link>
        </div>
      </div>
    );
  }

  // Registration form
  return (
    <form onSubmit={handleRegister}>
      <div className="flex flex-col justify-center max-w-md w-full min-h-screen mx-auto space-y-4">
        <div>
          <span className="text-[clamp(0.85rem,0.8vw,1rem)] font-medium tracking-[0.20em]">
            A WARM WELCOME TO
          </span>
          <br />
          <span className="peerprep-logo">PeerPrep</span>
        </div>

        {/* Shared error display for both validation & API errors */}
        {(validationError || error) && (
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
            <span>{validationError || error}</span>
          </div>
        )}

        <fieldset className="pb-3">
          {/* Name Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="first_name"
                className="fieldset-legend font-normal"
              >
                First Name
              </label>
              <input
                id="first_name"
                name="first_name"
                type="text"
                autoComplete="given-name"
                required
                className="input validator w-full"
                placeholder="First name"
                value={formData.first_name}
                onChange={handleInputChange}
                disabled={submitting}
              />
            </div>

            <div>
              <label
                htmlFor="last_name"
                className="fieldset-legend font-normal"
              >
                Last Name
              </label>
              <input
                id="last_name"
                name="last_name"
                type="text"
                autoComplete="family-name"
                required
                className="input validator w-full"
                placeholder="Last name"
                value={formData.last_name}
                onChange={handleInputChange}
                disabled={submitting}
              />
            </div>
          </div>

          {/* Email Field */}
          <label htmlFor="email" className="fieldset-legend font-normal">
            Email Address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="input validator w-full"
            placeholder="Enter your email"
            value={formData.email}
            onChange={handleInputChange}
            disabled={submitting}
          />

          {/* Password Field */}
          <label htmlFor="password" className="fieldset-legend font-normal">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            className="input validator w-full"
            placeholder="Create a password"
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
            <>
              <span className="loading loading-spinner loading-sm mr-2"></span>
              Creating account...
            </>
          ) : (
            'Register Account'
          )}
        </button>

        {/* Additional Register Link at Bottom */}
        <p className="text-center">
          <Link to="/auth/login" className="underline">
            Back to Login
          </Link>
        </p>
      </div>
    </form>
  );
}
