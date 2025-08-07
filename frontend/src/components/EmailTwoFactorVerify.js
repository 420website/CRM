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

  // Auto-send verification code when component mounts (same as EmailTwoFactorSetup)
  useEffect(() => {
    if (sessionToken && !codeSent && !sendingCode) {
      console.log('Auto-sending verification code on component mount');
      sendVerificationCode();
    }
  }, [sessionToken, codeSent, sendingCode]);

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
      setTimeLeft(60); // 1 minute = 60 seconds (changed from 180)
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
              📧 <strong>{adminEmail}</strong>
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
                  <li>• Check {adminEmail} for a 6-digit verification code</li>
                  <li>• Enter the code in the next screen to complete setup</li>
                  <li>• Codes expire after 1 minute for security {timeLeft > 0 && `(${formatTime(timeLeft)} remaining)`}</li>
                </ul>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              onClick={onCancel}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Navigate to actual verification input screen (this will be handled by parent component)
                const event = new Event('enterVerificationCode');
                document.dispatchEvent(event);
              }}
              className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
            >
              Enter Verification Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailTwoFactorVerify;