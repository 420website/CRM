import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  // Check if user is authenticated
  const isAuthenticated = () => {
    // Check for session storage flag
    const adminAuthenticated = sessionStorage.getItem('admin_authenticated');
    
    // Check for current user session
    const currentUser = sessionStorage.getItem('current_user');
    
    // User is authenticated if either flag is present
    return adminAuthenticated === 'true' || currentUser !== null;
  };

  // If not authenticated, redirect to admin PIN page
  if (!isAuthenticated()) {
    return <Navigate to="/admin-pin" replace />;
  }

  // If authenticated, render the protected component
  return children;
};

export default ProtectedRoute;