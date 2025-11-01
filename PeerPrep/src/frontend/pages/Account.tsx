/**
 * Account settings page
 *
 * This page displays and allows editing of a user's first name, last name and
 * email. The role is shown but not editable. Changes are saved via the
 * `userApi.updateUser` endpoint. Editing the email toggles an input into an
 * editable state and informs the user that re‑verification is required.
 */
import React, { useEffect, useState } from 'react';
import NavBar from '../components/NavBar';
import { NAV_BUTTONS } from '../config/NavConfig';
import { useAuth } from '../context/AuthContext';
import { userApi } from '../api/UserApi';
import { useNavigate } from 'react-router';

interface UpdateUserForm {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
}

function Account() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Local state for form fields
  const [updateUser, setUpdateUser] = useState<UpdateUserForm>({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [editEmail, setEditEmail] = useState<boolean>(false);
  const [passwordValidation, setPasswordValidation] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    numberOrSymbol: false,
  });
  const [submitting, setSubmitting] = useState(false);
  const [infoMsg, setInfoMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Populate form fields when user data is available
  useEffect(() => {
    if (user) {
      setUpdateUser({
        email: user.email ?? '',
        password: '',
        confirmPassword: '',
        first_name: user.first_name ?? '',
        last_name: user.last_name ?? '',
      });
    }
  }, [user]);

  // Extract role string for display
  const roleString = user?.role.role;

  /**
   * Validate password against defined criteria.
   *
   * @param password - The password string to validate
   * @returns Whether the password meets all criteria
   */
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

  /**
   * Handle input field changes and update local state accordingly.
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUpdateUser((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Validate password in real-time
    if (name === 'password') {
      validatePassword(value);
    }

    // Clear error when user starts typing
    if (infoMsg) setInfoMsg(null);
    if (errorMsg) setErrorMsg(null);
  };

  /**
   * Reset form fields to current user values and clear any status messages.
   */
  const handleCancel = () => {
    if (user) {
      setUpdateUser({
        email: user.email ?? '',
        password: '',
        confirmPassword: '',
        first_name: user.first_name ?? '',
        last_name: user.last_name ?? '',
      });
    }
    setEditEmail(false);
    setInfoMsg(null);
    setSuccessMsg(null);
    setErrorMsg(null);
  };

  /**
   * Persist the updated profile to the backend. Only send fields that have
   * actually changed to minimise payload size. Afterward, refresh the
   * displayed user information by reloading.
   */
  const handleSave = async () => {
    setSubmitting(true);
    if (!user) return;
    if (!updateUser.email || !updateUser.first_name || !updateUser.last_name) {
      setErrorMsg('Highlighted fields are required');
      setSubmitting(false);
      return;
    }
    const updateData: Record<string, string> = {};
    let emailModified = false;
    if (updateUser.first_name !== user.first_name)
      updateData.first_name = updateUser.first_name;
    if (updateUser.last_name !== user.last_name)
      updateData.last_name = updateUser.last_name;
    if (editEmail && updateUser.email !== user.email) {
      updateData.email = updateUser.email;
      emailModified = true;
    }
    if (updateUser.password) {
      if (updateUser.password !== updateUser.confirmPassword) {
        setErrorMsg('Passwords do not match');
        setSubmitting(false);
        return;
      }

      if (!validatePassword(updateUser.password)) {
        setErrorMsg('Password does not meet requirements');
        setSubmitting(false);
        return;
      }

      if (updateUser.email.includes(updateUser.password)) {
        setErrorMsg('Password should not contain your email address');
        setSubmitting(false);
        return;
      }
      updateData.password = updateUser.password;
    }

    if (Object.keys(updateData).length === 0) {
      setInfoMsg('No changes to save.');
      setSubmitting(false);
      return;
    }

    const { error } = await userApi.updateUser(updateData);
    if (error) {
      setErrorMsg(error);
      setSubmitting(false);
    } else {
      if (emailModified) {
        setSuccessMsg(
          'Changes saved successfully. You will be logged out in 5 seconds. Please check your updated email for a verification link.'
        );
        setTimeout(async () => {
          await logout();
          navigate('/auth/login');
        }, 5000);
      } else {
        setSuccessMsg('Changes saved successfully.');
        setTimeout(() => {
          navigate(0);
        }, 500);
      }
    }
  };

  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />
      <h1 className="text-6xl font-semibold p-2">Account Settings</h1>
      <main>
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {infoMsg && (
            <div className="alert alert-info alert-soft mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                className="h-6 w-6 shrink-0 stroke-current"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
              <span>{infoMsg}</span>
            </div>
          )}
          {successMsg && (
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
              <span>{successMsg}</span>
            </div>
          )}
          {errorMsg && (
            <div className="alert alert-error alert-soft mb-6">
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
              <span>{errorMsg}</span>
            </div>
          )}
          <p className="text-2xl p-2 font-light tracking-widest">
            Personal Information
          </p>
          <fieldset className="px-2">
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
                  value={updateUser.first_name}
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
                  value={updateUser.last_name}
                  onChange={handleInputChange}
                  disabled={submitting}
                />
              </div>
            </div>

            {/* Email Field */}
            <label htmlFor="email" className="fieldset-legend font-normal">
              Email Address
            </label>
            <div className="flex flex-col md:flex-row md:items-center md:gap-4">
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input validator w-full"
                placeholder="Enter your email"
                value={updateUser.email}
                onChange={handleInputChange}
                disabled={!editEmail || submitting}
              />
              <button
                type="button"
                className="btn btn-primary mt-2 md:mt-0"
                onClick={() => setEditEmail((prev) => !prev)}
              >
                {editEmail ? 'Cancel' : 'Edit Email'}
              </button>
            </div>
            {editEmail && (
              <div className="alert alert-error alert-soft my-4">
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
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span>
                  Editing your email will require re‑verification of your email
                  address and you will be logged out until it is verified.
                </span>
              </div>
            )}

            {/* Role Field */}
            <label htmlFor="email" className="fieldset-legend font-normal">
              Role
            </label>
            <input
              id="role"
              name="role"
              type="text"
              className="input input-bordered input-disabled w-full"
              value={roleString}
              disabled
            />
          </fieldset>
          <div role="separator" className="bg-slate-200 my-8 w-full h-px"></div>
          <p className="text-2xl p-2 font-light tracking-widest">
            Change password
          </p>
          <fieldset className="px-2">
            {/* Password Field */}
            <label htmlFor="password" className="fieldset-legend font-normal">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              className="input validator w-full"
              placeholder="New password"
              value={updateUser.password}
              onChange={handleInputChange}
              disabled={submitting}
            />

            {/* Password Requirements */}
            {updateUser.password && (
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
              className={`input validator w-full ${
                updateUser.confirmPassword &&
                updateUser.password !== updateUser.confirmPassword
                  ? 'border-error'
                  : updateUser.confirmPassword &&
                      updateUser.password === updateUser.confirmPassword
                    ? 'border-success'
                    : ''
              }`}
              placeholder="Confirm your password"
              value={updateUser.confirmPassword}
              onChange={handleInputChange}
              disabled={submitting}
            />
            {updateUser.confirmPassword &&
              updateUser.password !== updateUser.confirmPassword && (
                <p className="mt-1 text-xs text-error">
                  Passwords do not match
                </p>
              )}
          </fieldset>
          {/* Save & Cancel */}
          <div className="flex flex-col md:flex-row gap-4 mt-6 px-2">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSave}
            >
              {submitting ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              type="button"
              className="btn btn-outline"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Account;
