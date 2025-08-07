import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import EmailTwoFactorSetup from '../components/EmailTwoFactorSetup';
import EmailTwoFactorVerify from '../components/EmailTwoFactorVerify';

const AdminPIN = () => {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('pin'); // 'pin', '2fa-setup', '2fa-verify'
  const [sessionToken, setSessionToken] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const navigate = useNavigate();

  // Check if user is already authenticated and should bypass PIN/2FA
  useEffect(() => {
    // You can add logic here to check for existing authentication
    // For now, we'll rely on the normal PIN -> 2FA flow
  }, []);

  const handlePinSubmit = async (e) => {
    e.preventDefault();
    
    if (pin.length !== 4) {
      setError('PIN must be 4 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Use the new unified PIN verification endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/pin-verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid PIN');
      }

      const data = await response.json();
      
      console.log('PIN verification response:', data); // Debug log
      
      if (data.pin_valid) {
        setSessionToken(data.session_token);
        
        // Store user information for later use
        sessionStorage.setItem('current_user', JSON.stringify({
          user_id: data.user_id,
          user_type: data.user_type,
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email,
          permissions: data.permissions
        }));
        
        // Check if user needs email verification (first time users)
        if (data.needs_email_verification) {
          // First-time user - must verify email before getting access
          console.log('First-time user, requiring email verification');
          setAdminEmail(data.two_fa_email);
          setStep('2fa-setup'); // This will send verification email
        } else if (data.two_fa_enabled && data.two_fa_email) {
          // Returning user with 2FA already enabled - go directly to verification
          console.log('2FA enabled, going to verification screen');
          setAdminEmail(data.two_fa_email);
          setStep('2fa-verify');
        } else {
          // This shouldn't happen with the new logic, but fallback to setup
          console.log('Fallback to 2FA setup');
          setAdminEmail(data.two_fa_email);
          setStep('2fa-setup');
        }
      }
    } catch (err) {
      // Handle different error types
      if (err.message.includes("System locked") || err.message.includes("multiple failed PIN attempts")) {
        // This is a system lockout error - show special lockout message
        setError(`🔒 ${err.message}`);
        setStep('locked-out'); // New step for lockout display
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTwoFactorSetupComplete = (action) => {
    if (action === 'proceed-to-verify') {
      // Move to verification step
      setStep('2fa-verify');
    } else {
      // After 2FA setup is complete and verified, set authentication flag and go to admin menu
      sessionStorage.setItem('admin_authenticated', 'true');
      navigate('/admin-menu');
    }
  };

  const handleTwoFactorVerifySuccess = () => {
    // After 2FA verification, set authentication flag and go to admin menu
    sessionStorage.setItem('admin_authenticated', 'true');
    navigate('/admin-menu');
  };

  const handleCancel = () => {
    setStep('pin');
    setPin('');
    setError('');
    setSessionToken('');
    setAdminEmail('');
  };

  if (step === '2fa-setup') {
    return (
      <EmailTwoFactorSetup
        userEmail={adminEmail}
        sessionToken={sessionToken}
        onSetupComplete={handleTwoFactorSetupComplete}
        onCancel={handleCancel}
      />
    );
  }

  if (step === '2fa-verify') {
    return (
      <EmailTwoFactorVerify
        sessionToken={sessionToken}
        adminEmail={adminEmail}
        onVerificationSuccess={handleTwoFactorVerifySuccess}
        onCancel={handleCancel}
      />
    );
  }

  if (step === 'locked-out') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center mb-6">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m0 0v2m0-2h2m-2 0H8m4-9V6m0 0V4m0 2h2m-2 0H6" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">System Locked</h3>
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                {error}
              </div>
              
              <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-sm text-gray-800">
                  <p className="font-medium mb-2 text-gray-900">Need Help?</p>
                  <p className="mb-1 text-gray-600">For support with authentication issues:</p>
                  <p className="font-semibold text-black">📞 Call: 1-833-420-3733</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={() => {
                  setStep('pin');
                  setError('');
                  setPin('');
                }}
                className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Admin Access
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter your PIN to access the admin area
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handlePinSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="pin" className="block text-sm font-medium text-gray-700 text-center">
                4-Digit PIN
              </label>
              <div className="mt-1">
                <input
                  id="pin"
                  name="pin"
                  type="password"
                  maxLength="4"
                  pattern="[0-9]*"
                  inputMode="numeric"
                  required
                  value={pin}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    setPin(value);
                    setError('');
                  }}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-black focus:border-black focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
                  placeholder="****"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading || pin.length !== 4}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black disabled:bg-gray-300"
              >
                {loading ? 'Verifying...' : 'Continue'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <button
              onClick={() => navigate('/')}
              className="w-full text-center text-sm text-gray-600 hover:text-gray-800"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPIN;