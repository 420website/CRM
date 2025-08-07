import React, { useState, useEffect } from 'react';

const EmailTwoFactorSetup = ({ onSetupComplete, onCancel, userEmail, sessionToken }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('sending'); // 'sending', 'verify', 'error'
  const [showInputScreen, setShowInputScreen] = useState(false);
  const [emailCode, setEmailCode] = useState('');
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  // Use the provided userEmail or fallback to admin email
  const emailToUse = userEmail || 'support@my420.ca';

  // Countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  useEffect(() => {
    // Always send verification code when component mounts with valid session token
    if (sessionToken) {
      setupEmailTwoFactorAndSendCode();
    }
  }, [sessionToken]);

  const setupEmailTwoFactorAndSendCode = async () => {
    // Simple loading guard to prevent multiple simultaneous calls
    if (loading) {
      console.log('Setup already in progress, skipping...');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Send verification code directly (works for both user and admin sessions)
      const sendCodeResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/send-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken }),
      });

      if (!sendCodeResponse.ok) {
        const errorData = await sendCodeResponse.json();
        throw new Error(errorData.detail || 'Failed to send verification code');
      }

      // Move to verification step and set 1-minute timer
      setStep('verify');
      setTimeLeft(60); // 1 minute = 60 seconds
    } catch (err) {
      console.error('❌ Setup error:', err.message);
      setError(err.message);
      setStep('error');
    } finally {
      setLoading(false);
    }
  };

  // Redirect to verification component
  const handleProceedToVerification = () => {
    // Instead of calling parent, show input screen directly
    setShowInputScreen(true);
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    
    if (!emailCode || emailCode.length !== 6) {
      setError('Please enter the 6-digit verification code');
      return;
    }

    setVerifyLoading(true);
    setError('');

    try {
      // Check if we're in development mode and using the test code
      const isDevelopment = process.env.REACT_APP_DEV_MODE === 'true';
      if (isDevelopment && emailCode === '123456') {
        // Simulate successful verification in development
        console.log('Development mode: Using test code 123456');
        onSetupComplete('dev-session-token');
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
      onSetupComplete(data.session_token);
    } catch (err) {
      setError(err.message);
      setEmailCode(''); // Clear the code on error
    } finally {
      setVerifyLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleVerify(e);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
            <p className="text-lg font-medium text-gray-900">Setting up Two-Factor Authentication...</p>
            <p className="text-sm text-gray-600 mt-2">Please wait while we configure your secure login.</p>
          </div>
        </div>
      </div>
    );
  }

  // Show input screen when user clicks "Enter Verification Code"
  if (showInputScreen) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Enter Verification Code
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter the 6-digit code sent to {emailToUse}
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
                {error}
              </div>
            )}

            {timeLeft > 0 && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      Code expires in <strong>{formatTime(timeLeft)}</strong>
                    </p>
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleVerify} className="space-y-6">
              <div>
                <label htmlFor="email-code" className="block text-sm font-medium text-gray-700 text-center">
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
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setShowInputScreen(false)}
                  className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={verifyLoading || emailCode.length !== 6}
                  className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
                >
                  {verifyLoading ? 'Verifying...' : 'Verify'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'error') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center mb-6">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Security Authentication</h3>
              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}
              
              <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-sm text-gray-800">
                  <p className="font-medium mb-2 text-gray-900">Need Help?</p>
                  <p className="mb-1 text-gray-600">For support with authentication issues:</p>
                  <p className="font-semibold text-black">📞 Call: 1-833-420-3733</p>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={onCancel}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={setupEmailTwoFactorAndSendCode}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show verification prompt instead of success screen
  if (step === 'verify') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center mb-6">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Verification Code Sent</h3>
              <p className="text-sm text-gray-600 mt-2">
                A 6-digit verification code has been sent to:
              </p>
              <p className="text-sm font-medium text-gray-900 mt-1">
                📧 <strong>{emailToUse}</strong>
              </p>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3 text-sm text-gray-600">
                  <p className="font-medium text-gray-900 mb-1">Next Steps:</p>
                  <ul className="space-y-1">
                    <li>• Check {emailToUse} for a 6-digit verification code</li>
                    <li>• Enter the code in the next screen to complete setup</li>
                    <li>• Codes expire after 1 minute for security</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={onCancel}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={handleProceedToVerification}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
              >
                Enter Verification Code
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null; // This should not be reached
};

export default EmailTwoFactorSetup;