import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requirePermissions = null }) => {
  const { isFullyAuthenticated, hasTabPermissions, hasPermission, loading, isAdmin } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If not fully authenticated, redirect to admin PIN page
  if (!isFullyAuthenticated()) {
    return <Navigate to="/admin-pin" replace />;
  }

  // Check permission-based access for specific routes
  const pathname = location.pathname;
  
  // Dashboard and Registration routes require tab permissions (unless admin)
  if ((pathname.includes('/admin-dashboard') || pathname.includes('/admin-register') || pathname.includes('/admin-edit')) && !isAdmin()) {
    if (!hasTabPermissions()) {
      return <Navigate to="/admin-menu" replace />;
    }
  }

  // User Management is admin-only
  if (pathname.includes('/admin-users') && !isAdmin()) {
    return <Navigate to="/admin-menu" replace />;
  }

  // Check specific permissions if required
  if (requirePermissions && !isAdmin()) {
    const hasRequiredPermissions = Array.isArray(requirePermissions) 
      ? requirePermissions.some(permission => hasPermission(permission))
      : hasPermission(requirePermissions);
    
    if (!hasRequiredPermissions) {
      return <Navigate to="/admin-menu" replace />;
    }
  }

  // If all checks pass, render the protected component
  return children;
};

export default ProtectedRoute;