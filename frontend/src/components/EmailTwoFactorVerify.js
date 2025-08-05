import React, { useState, useEffect } from 'react';

const EmailTwoFactorVerify = ({ sessionToken, adminEmail, onVerificationSuccess, onCancel }) => {
  const [emailCode, setEmailCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [error, setError] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const sendVerificationCode = async () => {
    // Prevent multiple simultaneous sends
    if (sendingCode) {
      console.log('Already sending code, skipping...');
      return;
    }

    setSendingCode(true);
    setError('');

    try {
      console.log('Sending verification code to:', adminEmail);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/send-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send verification code');
      }

      const data = await response.json();
      setCodeSent(true);
      setTimeLeft(180); // 3 minutes = 180 seconds
      console.log('Verification code sent successfully');
    } catch (err) {
      setError(err.message);
      console.error('Failed to send verification code:', err);
    } finally {
      setSendingCode(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    
    if (!emailCode || emailCode.length !== 6) {
      setError('Please enter the 6-digit verification code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Check if we're in development mode and using the test code
      const isDevelopment = process.env.REACT_APP_DEV_MODE === 'true';
      if (isDevelopment && emailCode === '123456') {
        // Simulate successful verification in development
        console.log('Development mode: Using test code 123456');
        onVerificationSuccess('dev-session-token');
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_code: emailCode,
          session_token: sessionToken,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      const data = await response.json();
      
      // For new users, mark their email as verified
      const currentUser = JSON.parse(sessionStorage.getItem('current_user') || '{}');
      if (currentUser.user_type === 'user' && currentUser.user_id) {
        try {
          await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/${currentUser.user_id}/mark-email-verified`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });
          console.log('User marked as email verified');
        } catch (markError) {
          console.error('Failed to mark user as email verified:', markError);
          // Don't block the flow, just log the error
        }
      }
      
      onVerificationSuccess(data.session_token);
    } catch (err) {
      setError(err.message);
      setEmailCode(''); // Clear the code on error
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleVerify(e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Check Your Email
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          We've sent a verification code to your email
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {codeSent && (
            <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-gray-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <p className="text-sm text-gray-900">
                  Verification code sent to <strong>{adminEmail}</strong>
                </p>
              </div>
              {timeLeft > 0 && (
                <p className="text-xs text-gray-600 mt-1">
                  Code expires in {formatTime(timeLeft)}
                </p>
              )}
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label htmlFor="email-code" className="block text-sm font-medium text-gray-700">
                6-digit verification code
              </label>
              <div className="mt-1">
                <input
                  id="email-code"
                  type="text"
                  maxLength="6"
                  pattern="[0-9]*"
                  inputMode="numeric"
                  value={emailCode}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    setEmailCode(value);
                    setError('');
                  }}
                  onKeyPress={handleKeyPress}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest font-mono"
                  placeholder="000000"
                  autoComplete="one-time-code"
                />
              </div>
              <p className="mt-2 text-xs text-gray-500 text-center">
                Enter the 6-digit code from your email
              </p>
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || emailCode.length !== 6}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
              >
                {loading ? 'Verifying...' : 'Verify'}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={sendVerificationCode}
                disabled={sendingCode || timeLeft > 0}
                className="text-sm text-gray-600 hover:text-gray-800 underline disabled:text-gray-400 disabled:no-underline"
              >
                {sendingCode ? 'Sending...' : 
                 timeLeft > 0 ? `Request new code in ${formatTime(timeLeft)}` :
                 'Resend verification code'}
              </button>
            </div>
          </form>

          <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              💡 Didn't receive the email?
            </h4>
            <ul className="text-xs text-gray-700 space-y-1">
              <li>• Check your spam/junk folder</li>
              <li>• Make sure the email address is correct</li>
              <li>• Wait a few minutes and check again</li>
              <li>• Contact support if the issue persists</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailTwoFactorVerify;