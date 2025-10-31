import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router';
import { userApi } from '../api/UserApi';

export default function Verify() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<
    'idle' | 'loading' | 'success' | 'error'
  >('idle');
  const [message, setMessage] = useState<string>('');
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setMessage('No verification token provided in the URL.');
      setErrorDetails(
        'Please check your verification email and use the correct link.'
      );
      setStatus('error');
      return;
    }

    const verifyToken = async () => {
      setStatus('loading');
      setMessage('');
      setErrorDetails(null);

      try {
        const response = await userApi.verifyEmail(token);
        console.log('Verification response:', response);
        if (response.error) {
          // Handle API errors returned from backend
          setMessage('Verification failed');
          setErrorDetails(response.error);
          setStatus('error');
        } else if (response.data) {
          // Success case
          setMessage('Your email has been verified successfully!');
          setStatus('success');
        } else {
          // Unexpected response structure
          setMessage('Verification completed');
          setStatus('success');
        }
      } catch (error: any) {
        // Handle unexpected errors (network errors, parsing errors, etc.)
        console.error('Verification error:', error);
        setMessage('An unexpected error occurred');
        setErrorDetails(error.detail);
        setStatus('error');
      }
    };

    verifyToken();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200 p-4">
      <div className="card w-full max-w-md bg-base-100 shadow-xl">
        <div className="card-body items-center text-center">
          {status === 'loading' && (
            <>
              <span className="loading loading-spinner loading-lg text-primary"></span>
              <h2 className="card-title text-2xl mt-4">Verifying Account</h2>
              <p className="text-base-content/70">
                Please wait while we verify your email...
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="text-6xl mb-4 text-success">✓</div>
              <h2 className="card-title text-2xl">Verification Successful!</h2>
              <p className="text-base-content/70 mt-2">{message}</p>
              <div className="card-actions mt-6 w-full">
                <Link to="/auth/login" className="btn btn-primary w-full">
                  Continue to Login
                </Link>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="text-6xl mb-4 text-error">✗</div>
              <h2 className="card-title text-2xl mb-4">
                {message || 'Verification Failed'}
              </h2>

              <div className="alert alert-error shadow-lg">
                <div className="flex flex-col items-start w-full">
                  <div className="flex items-center gap-2 mb-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="stroke-current shrink-0 h-6 w-6"
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
                    <span className="font-semibold">Error Details</span>
                  </div>
                  <p className="text-sm text-left">
                    {errorDetails || 'An unknown error occurred.'}
                  </p>
                </div>
              </div>

              {/* Additional help text */}
              <div className="text-sm text-base-content/70 mt-4 text-left w-full space-y-2">
                <div className="font-semibold">Possible issues:</div>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>The verification link may have expired</li>
                  <li>The link may have already been used</li>
                  <li>The token in the URL may be invalid or incomplete</li>
                </ul>
              </div>

              <div className="card-actions mt-6 w-full flex-col gap-2">
                <Link to="/auth/register" className="btn btn-primary w-full">
                  Register New Account
                </Link>
                <Link to="/auth/login" className="btn btn-outline w-full">
                  Back to Login
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
