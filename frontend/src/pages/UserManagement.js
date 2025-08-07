import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

const UserManagement = () => {
  const navigate = useNavigate();
  
  // Security check - Only allow secret admin (PIN 0224) to access User Management
  useEffect(() => {
    const currentUser = sessionStorage.getItem('current_user');
    if (currentUser) {
      try {
        const userData = JSON.parse(currentUser);
        // Only allow access if user_id is "admin" and user_type is "admin" (PIN 0224 user)
        if (!(userData.user_id === "admin" && userData.user_type === "admin")) {
          alert('Access denied: You do not have permission to access User Management.');
          navigate('/admin-menu');
          return;
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        alert('Authentication error. Please log in again.');
        navigate('/admin');
        return;
      }
    } else {
      alert('No authentication found. Please log in again.');
      navigate('/admin');
      return;
    }
  }, [navigate]);
  
  // State management
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddUser, setShowAddUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    pin: '',
    permissions: {}
  });

  // API base URL
  const API_BASE = useMemo(() => {
    return process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  }, []);

  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/users`);
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        throw new Error('Failed to fetch users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Load users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  // Handle permissions checkbox changes
  const handlePermissionChange = (tab) => {
    setFormData(prev => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [tab]: !prev.permissions[tab]
      }
    }));
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      pin: '',
      permissions: {}
    });
    setEditingUser(null);
    setShowAddUser(false);
  };

  // Handle add user
  const handleAddUser = async (e) => {
    e.preventDefault();
    
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.phone || !formData.pin) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.pin.length !== 10 || !/^\d{10}$/.test(formData.pin)) {
      setError('PIN must be exactly 10 digits');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ User ${formData.firstName} ${formData.lastName} created successfully!`);
        resetForm();
        fetchUsers(); // Refresh the list
      } else {
        const errorText = await response.text();
        setError(`Failed to create user: ${errorText}`);
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle edit user
  const handleEditUser = (user) => {
    setFormData({
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email,
      phone: user.phone,
      pin: user.pin,
      permissions: user.permissions || {}
    });
    setEditingUser(user);
    setShowAddUser(true);
  };

  // Handle update user
  const handleUpdateUser = async (e) => {
    e.preventDefault();
    
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.phone || !formData.pin) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.pin.length !== 10 || !/^\d{10}$/.test(formData.pin)) {
      setError('PIN must be exactly 10 digits');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/users/${editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ User ${formData.firstName} ${formData.lastName} updated successfully!`);
        resetForm();
        fetchUsers(); // Refresh the list
      } else {
        const errorText = await response.text();
        setError(`Failed to update user: ${errorText}`);
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete user
  const handleDeleteUser = async (user) => {
    const confirmed = window.confirm(`Delete user ${user.firstName} ${user.lastName}?\n\nThis action cannot be undone.`);
    
    if (!confirmed) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/users/${user.id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert(`✅ User ${user.firstName} ${user.lastName} deleted successfully!`);
        fetchUsers(); // Refresh the list
      } else {
        const errorText = await response.text();
        setError(`Failed to delete user: ${errorText}`);
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    navigate('/admin-menu');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">User Management</h1>
          <div className="flex gap-2">
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-2 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Admin Menu
            </button>
            <button
              onClick={() => setShowAddUser(!showAddUser)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {showAddUser ? 'Cancel' : 'Add User'}
            </button>
          </div>
        </div>

        {/* Add/Edit User Form */}
        {showAddUser && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingUser ? 'Edit User' : 'Add New User'}
            </h2>
            
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <form onSubmit={editingUser ? handleUpdateUser : handleAddUser}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name *
                  </label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ height: '40px' }}
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ height: '40px' }}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ height: '40px' }}
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="(XXX) XXX-XXXX"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ height: '40px' }}
                    required
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  10-Digit PIN *
                </label>
                <input
                  type="password"
                  name="pin"
                  value={formData.pin}
                  onChange={handleInputChange}
                  maxLength="10"
                  pattern="[0-9]{10}"
                  className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{ height: '40px' }}
                  placeholder="0000000000"
                  required
                />
                <p className="text-xs text-gray-600 mt-1">Must be exactly 10 digits</p>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {loading ? 'Saving...' : editingUser ? 'Update User' : 'Create User'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors text-sm font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Users List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Users ({users.length})</h2>
            <button
              onClick={fetchUsers}
              disabled={loading}
              className="bg-gray-100 text-gray-700 py-1 px-3 rounded-md hover:bg-gray-200 transition-colors text-sm disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {loading && users.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-600">Loading users...</div>
            </div>
          ) : (
            <div>
              {users.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-600">No users found. Create your first user to get started.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {users.map((user) => (
                    <div key={user.id} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {user.firstName} {user.lastName}
                          </h3>
                          <div className="text-sm text-gray-600 mt-1 space-y-1">
                            <p><strong>Email:</strong> {user.email}</p>
                            <p><strong>Phone:</strong> {user.phone}</p>
                            <p><strong>PIN:</strong> {user.pin}</p>
                            <p><strong>Created:</strong> {new Date(user.created_at).toLocaleString()}</p>
                            <p className="text-xs text-gray-500">ID: {user.id}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex gap-2 mt-4">
                        <button
                          onClick={() => handleEditUser(user)}
                          className="bg-black hover:bg-gray-800 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user)}
                          className="bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagement;