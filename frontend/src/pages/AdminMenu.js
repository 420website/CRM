import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminMenu = () => {
  const navigate = useNavigate();
  const [isSecretAdmin, setIsSecretAdmin] = useState(false);
  const [hasTabPermissions, setHasTabPermissions] = useState(false);

  // Get current user permissions
  const getCurrentUserPermissions = () => {
    try {
      const currentUser = sessionStorage.getItem('current_user');
      if (currentUser) {
        const userData = JSON.parse(currentUser);
        return userData.permissions || {};
      }
    } catch (error) {
      console.error('Error getting user permissions:', error);
    }
    return {};
  };

  // Check if user has any tab permissions
  const checkTabPermissions = () => {
    const permissions = getCurrentUserPermissions();
    const tabPermissions = ['Client', 'Tests', 'Medication', 'Dispensing', 'Notes', 'Activities', 'Interactions', 'Attachments'];
    
    // Check if user has permission for any tab
    return tabPermissions.some(tab => permissions[tab] === true);
  };

  useEffect(() => {
    // Check if current user is the secret admin (PIN 0224)
    const currentUser = sessionStorage.getItem('current_user');
    if (currentUser) {
      try {
        const userData = JSON.parse(currentUser);
        
        // Check if secret admin
        const isAdmin = userData.user_id === "admin" && userData.user_type === "admin";
        setIsSecretAdmin(isAdmin);
        
        // Admin always has tab permissions, for others check their permissions
        if (isAdmin) {
          setHasTabPermissions(true);
        } else {
          setHasTabPermissions(checkTabPermissions());
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        setIsSecretAdmin(false);
        setHasTabPermissions(false);
      }
    }
  }, []);

  const goBack = () => {
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
            <button
              onClick={handleDashboard}
              className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
              style={{ backgroundColor: '#000000' }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
            >
              📊 Dashboard
            </button>

            <button
              onClick={handleRegistration}
              className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
              style={{ backgroundColor: '#000000' }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#1f2937'}
              onMouseLeave={(e) => e.target.style.backgroundColor = '#000000'}
            >
              📝 Registration
            </button>

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
            {isSecretAdmin && (
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