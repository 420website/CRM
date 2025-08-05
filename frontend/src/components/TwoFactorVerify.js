import React, { useState } from 'react';

const TwoFactorVerify = ({ sessionToken, onVerificationSuccess, onCancel }) => {
  const [totpCode, setTotpCode] = useState('');
  const [backupCode, setBackupCode] = useState('');
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleVerify = async () => {
    const codeToVerify = useBackupCode ? backupCode.trim() : totpCode;
    
    if (!codeToVerify) {
      setError('Please enter a verification code');
      return;
    }

    if (!useBackupCode && codeToVerify.length !== 6) {
      setError('TOTP code must be 6 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/2fa/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_token: sessionToken,
          totp_code: useBackupCode ? null : totpCode,
          backup_code: useBackupCode ? backupCode.trim() : null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      const data = await response.json();
      onVerificationSuccess(data.session_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleVerify();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Two-Factor Authentication
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your authentication code to continue
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {!useBackupCode ? (
              <>
                <div>
                  <label htmlFor="totp-code" className="block text-sm font-medium text-gray-700">
                    6-digit code from authenticator app
                  </label>
                  <input
                    id="totp-code"
                    type="text"
                    maxLength="6"
                    pattern="[0-9]*"
                    inputMode="numeric"
                    value={totpCode}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '');
                      setTotpCode(value);
                      setError('');
                    }}
                    onKeyPress={handleKeyPress}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
                    placeholder="000000"
                    autoComplete="one-time-code"
                  />
                </div>
                
                <button
                  type="button"
                  onClick={() => setUseBackupCode(true)}
                  className="text-sm text-gray-600 hover:text-gray-800 underline"
                >
                  Use backup code instead
                </button>
              </>
            ) : (
              <>
                <div>
                  <label htmlFor="backup-code" className="block text-sm font-medium text-gray-700">
                    Backup recovery code
                  </label>
                  <input
                    id="backup-code"
                    type="text"
                    value={backupCode}
                    onChange={(e) => {
                      setBackupCode(e.target.value);
                      setError('');
                    }}
                    onKeyPress={handleKeyPress}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center font-mono"
                    placeholder="Enter backup code"
                  />
                </div>
                
                <button
                  type="button"
                  onClick={() => setUseBackupCode(false)}
                  className="text-sm text-gray-600 hover:text-gray-800 underline"
                >
                  Use authenticator app instead
                </button>
              </>
            )}

            <div className="flex space-x-4">
              <button
                onClick={onCancel}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                onClick={handleVerify}
                disabled={loading || (!useBackupCode && totpCode.length !== 6) || (useBackupCode && !backupCode.trim())}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
              >
                {loading ? 'Verifying...' : 'Verify'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoFactorVerify;