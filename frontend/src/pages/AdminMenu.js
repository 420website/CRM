import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminMenu = () => {
  const navigate = useNavigate();
  const { isAdmin, hasTabPermissions, logout } = useAuth();

  // Get current user permissions
  const getCurrentUserPermissions = () => {
    // This function is no longer needed as permissions are in the context
    return {};
  };

  // Check if user has any tab permissions
  const checkTabPermissions = () => {
    // This function is no longer needed as hasTabPermissions is in the context
    return hasTabPermissions();
  };

  useEffect(() => {
    // No need to check permissions here as they're handled by the context
    // and ProtectedRoute component
  }, []);

  const goBack = () => {
    navigate('/');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleDashboard = () => {
    // Navigate to dashboard (authentication already verified by ProtectedRoute)
    navigate('/admin-dashboard');
  };

  const handleRegistration = () => {
    // Navigate to registration (authentication already verified by ProtectedRoute)
    navigate('/admin-register');
  };

  const handleAnalytics = () => {
    // Navigate to Analytics page
    navigate('/admin-analytics');
  };

  const handleUsers = () => {
    // Navigate to User Management page
    navigate('/admin-users');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Menu</h1>
            <p className="text-gray-600">Choose an option to continue:</p>
          </div>

          {/* Menu Options */}
          <div className="space-y-6">
            {/* Dashboard - Only show if user has tab permissions */}
            {hasTabPermissions() && (
              <button
                onClick={handleDashboard}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: '#000000' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
              >
                📊 Dashboard
              </button>
            )}

            {/* Registration - Only show if user has tab permissions */}
            {hasTabPermissions() && (
              <button
                onClick={handleRegistration}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: '#000000' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
              >
                📝 Registration
              </button>
            )}

            {/* Analytics - Always available */}
            <button
              onClick={handleAnalytics}
              className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
              style={{ backgroundColor: '#000000' }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
            >
              🤖 Analytics
            </button>

            {/* Users button - Only visible to secret admin (PIN 0224) */}
            {isAdmin() && (
              <button
                onClick={handleUsers}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: '#000000' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
              >
                👥 Users
              </button>
            )}

            {/* Logout button */}
            <button
              onClick={handleLogout}
              className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors bg-red-600 hover:bg-red-700"
            >
              🚪 Logout
            </button>
          </div>

          {/* Back Button */}
          <div className="mt-8 text-center">
            <button
              onClick={goBack}
              className="text-gray-600 hover:text-gray-800 text-sm"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminMenu;