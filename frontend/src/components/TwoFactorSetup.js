import React, { useState, useEffect } from 'react';

const TwoFactorSetup = ({ onSetupComplete, onCancel }) => {
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('setup'); // 'setup', 'verify', 'complete'
  const [backupCodes, setBackupCodes] = useState([]);

  useEffect(() => {
    initializeSetup();
  }, []);

  const initializeSetup = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to initialize 2FA setup');

      const data = await response.json();
      setSetupData(data);
      setBackupCodes(data.backup_codes);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const verifySetup = async () => {
    if (verificationCode.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/verify-setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ totp_code: verificationCode }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      setStep('complete');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = () => {
    onSetupComplete();
  };

  if (loading && !setupData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
          <p>Initializing 2FA setup...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Two-Factor Authentication Setup
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Secure your admin account with 2FA
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {step === 'setup' && setupData && (
            <>
              <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Step 1: Scan QR Code
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Use Google Authenticator, Authy, or another TOTP app to scan this QR code:
                </p>
                <img 
                  src={setupData.qr_code_data} 
                  alt="2FA QR Code" 
                  className="mx-auto mb-4 border rounded"
                />
                <div className="text-xs text-gray-500 mb-4">
                  Can't scan? Manual entry key: <br />
                  <code className="bg-gray-100 px-2 py-1 rounded font-mono break-all">
                    {setupData.totp_secret}
                  </code>
                </div>
              </div>

              <div className="mb-6">
                <label htmlFor="verification-code" className="block text-sm font-medium text-gray-700">
                  Enter 6-digit code from your authenticator app:
                </label>
                <input
                  id="verification-code"
                  type="text"
                  maxLength="6"
                  pattern="[0-9]*"
                  inputMode="numeric"
                  value={verificationCode}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    setVerificationCode(value);
                    setError('');
                  }}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
                  placeholder="000000"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={onCancel}
                  className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={verifySetup}
                  disabled={loading || verificationCode.length !== 6}
                  className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
                >
                  {loading ? 'Verifying...' : 'Verify & Enable'}
                </button>
              </div>
            </>
          )}

          {step === 'complete' && (
            <>
              <div className="text-center mb-6">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  2FA Enabled Successfully!
                </h3>
                <p className="text-sm text-gray-600 mt-2">
                  Your admin account is now protected with two-factor authentication.
                </p>
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-900 mb-2">
                  ⚠️ Save Your Backup Codes
                </h4>
                <p className="text-xs text-gray-600 mb-3">
                  Store these codes in a safe place. You can use them to access your account if you lose your authenticator device.
                </p>
                <div className="bg-gray-50 p-3 rounded border max-h-40 overflow-y-auto">
                  {backupCodes.map((code, index) => (
                    <div key={index} className="font-mono text-sm py-1">
                      {code}
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleComplete}
                className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
              >
                Continue to Admin Dashboard
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TwoFactorSetup;