import React, { useState, useEffect } from 'react';

const EmailTwoFactorSetup = ({ onSetupComplete, onCancel, userEmail, sessionToken }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('sending'); // 'sending', 'verify', 'error'

  // Use the provided userEmail or fallback to admin email
  const emailToUse = userEmail || 'support@my420.ca';

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

    // Don't show loading screen - go directly to verification step
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

      // Move to verification step without showing loading
      setStep('verify');
    } catch (err) {
      console.error('❌ Setup error:', err.message);
      setError(err.message);
      setStep('error');
    }
  };

  // Redirect to verification component
  const handleProceedToVerification = () => {
    // Call the parent to move to verification step
    if (onSetupComplete) {
      onSetupComplete('proceed-to-verify');
    }
  };

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