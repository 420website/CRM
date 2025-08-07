import React, { useState, useEffect, useRef, useMemo } from "react";
import { useNavigate } from "react-router-dom";

// Virtual Scrolling Component for better performance
const VirtualizedList = ({ items, renderItem, itemHeight = 100 }) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(600);
  const containerRef = useRef(null);

  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(visibleStart + Math.ceil(containerHeight / itemHeight) + 1, items.length);

  const visibleItems = items.slice(visibleStart, visibleEnd);
  const totalHeight = items.length * itemHeight;
  const offsetY = visibleStart * itemHeight;

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      setContainerHeight(container.clientHeight);
    }
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ height: '600px', overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={item.id || visibleStart + index} style={{ height: itemHeight }}>
              {renderItem(item, visibleStart + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  
  // Core state
  const [activeTab, setActiveTab] = useState('activities');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20); // Fixed page size for optimal performance
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  
  // Data state - now paginated
  const [currentData, setCurrentData] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    pending_registrations: 0,
    submitted_registrations: 0,
    total_activities: 0
  });
  
  // Search and filter state
  const [searchName, setSearchName] = useState('');
  const [searchDate, setSearchDate] = useState('');
  const [searchDisposition, setSearchDisposition] = useState('');
  const [searchReferralSite, setSearchReferralSite] = useState('');
  const [activitySearchTerm, setActivitySearchTerm] = useState('');
  const [activityStatusFilter, setActivityStatusFilter] = useState('all');
  
  // Photo lazy loading state
  const [loadedPhotos, setLoadedPhotos] = useState({});
  const [loadingPhotos, setLoadingPhotos] = useState(new Set());
  
  // Action states
  const [finalizingId, setFinalizingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [revertingId, setRevertingId] = useState(null);

  // Memoized API base URL
  const API_BASE = useMemo(() => {
    return process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  }, []);

  // Load dashboard statistics efficiently
  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin-dashboard-stats`);
      if (response.ok) {
        const stats = await response.json();
        setDashboardStats(stats);
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  // Optimized data fetching with pagination
  const fetchPaginatedData = async (tab = activeTab, page = currentPage, forceRefresh = false) => {
    if (loading && !forceRefresh) return; // Prevent duplicate requests
    
    setLoading(true);
    setError(null);
    
    try {
      let url = '';
      let params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      });
      
      if (tab === 'pending') {
        url = `${API_BASE}/api/admin-registrations-pending-optimized`;
        if (searchName) params.append('search_name', searchName);
        if (searchDate) params.append('search_date', searchDate);
        if (searchDisposition) params.append('search_disposition', searchDisposition);
        if (searchReferralSite) params.append('search_referral_site', searchReferralSite);
      } else if (tab === 'submitted') {
        url = `${API_BASE}/api/admin-registrations-submitted-optimized`;
        if (searchName) params.append('search_name', searchName);
        if (searchDate) params.append('search_date', searchDate);
        if (searchDisposition) params.append('search_disposition', searchDisposition);
        if (searchReferralSite) params.append('search_referral_site', searchReferralSite);
      } else if (tab === 'activities') {
        url = `${API_BASE}/api/admin-activities-optimized`;
        if (activitySearchTerm) params.append('search_term', activitySearchTerm);
        if (searchDate) params.append('search_date', searchDate);
        if (activityStatusFilter !== 'all') params.append('status_filter', activityStatusFilter);
      }
      
      const response = await fetch(`${url}?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (tab === 'activities') {
          setCurrentData(data.activities || []);
        } else {
          setCurrentData(data.data || []);
        }
        
        // Update pagination metadata
        if (data.pagination) {
          setCurrentPage(data.pagination.current_page);
          setTotalPages(data.pagination.total_pages);
          setTotalRecords(data.pagination.total_records);
        }
      } else {
        throw new Error('Failed to fetch data');
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
      setError(`Failed to load ${tab} data. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  // Lazy load photo for a specific registration
  const loadPhoto = async (registrationId) => {
    if (loadedPhotos[registrationId] || loadingPhotos.has(registrationId)) {
      return;
    }
    
    setLoadingPhotos(prev => new Set(prev).add(registrationId));
    
    try {
      const response = await fetch(`${API_BASE}/api/admin-registration/${registrationId}/photo`);
      if (response.ok) {
        const data = await response.json();
        setLoadedPhotos(prev => ({
          ...prev,
          [registrationId]: data.photo
        }));
      }
    } catch (error) {
      console.error('Error loading photo:', error);
    } finally {
      setLoadingPhotos(prev => {
        const newSet = new Set(prev);
        newSet.delete(registrationId);
        return newSet;
      });
    }
  };

  // Initial load
  useEffect(() => {
    window.scrollTo(0, 0);
    fetchDashboardStats();
    fetchPaginatedData(activeTab, 1, true);
  }, []);

  // Handle tab changes
  useEffect(() => {
    setCurrentPage(1); // Reset to first page when changing tabs
    fetchPaginatedData(activeTab, 1, true);
  }, [activeTab]);

  // Handle search changes with debouncing
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      setCurrentPage(1); // Reset to first page when searching
      fetchPaginatedData(activeTab, 1, true);
    }, 300); // 300ms debounce
    
    return () => clearTimeout(debounceTimer);
  }, [searchName, searchDate, searchDisposition, searchReferralSite, activitySearchTerm, activityStatusFilter]);

  // Handle page changes with scroll to top
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages && !loading) {
      fetchPaginatedData(activeTab, newPage, true);
      // Scroll to top of page for easy navigation
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Optimized search handlers
  const handleNameSearch = (value) => {
    setSearchName(value);
  };

  const handleDateSearch = (value) => {
    setSearchDate(value);
  };

  const handleDispositionSearch = (value) => {
    setSearchDisposition(value);
  };

  const handleReferralSiteSearch = (value) => {
    setSearchReferralSite(value);
  };

  const clearAllFilters = () => {
    setSearchName('');
    setSearchDate('');
    setSearchDisposition('');
    setSearchReferralSite('');
    setActivitySearchTerm('');
    setActivityStatusFilter('all');
  };

  // Optimized action handlers
  const handleDelete = async (registrationId, firstName, lastName) => {
    const confirmed = window.confirm(`Delete registration for ${firstName} ${lastName}?\n\nThis action cannot be undone.`);
    
    if (!confirmed) return;
    
    try {
      setDeletingId(registrationId);
      
      // Optimistic UI update - immediately remove from current list
      const originalData = [...currentData];
      const updatedData = currentData.filter(item => item.id !== registrationId);
      setCurrentData(updatedData);
      
      const response = await fetch(`${API_BASE}/api/admin-registration/${registrationId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        alert(`✅ ${firstName} ${lastName} deleted successfully!`);
        
        // Sequential refresh to prevent race conditions
        await fetchDashboardStats();
        await fetchPaginatedData(activeTab, currentPage, true);
        
      } else {
        // Revert optimistic update on failure
        setCurrentData(originalData);
        const errorText = await response.text();
        alert(`❌ Failed to delete: ${errorText}`);
      }
    } catch (error) {
      // Revert optimistic update on network error
      const originalData = currentData.filter(item => item.id !== registrationId);
      if (originalData.length !== currentData.length) {
        // Need to restore original data
        await fetchPaginatedData(activeTab, currentPage, true);
      }
      alert(`❌ Network error: ${error.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const handleFinalize = async (registrationId, firstName, lastName, photo) => {
    try {
      const photoText = photo ? " with photo attachment" : "";
      const proceed = window.confirm(`Finalize registration for ${firstName} ${lastName}?\n\nThis will send the email notification${photoText}.`);
      
      if (!proceed) return;
      
      setFinalizingId(registrationId);
      setError(null);
      
      // Optimistic UI update - immediately remove from pending list
      const originalData = [...currentData];
      const updatedData = currentData.filter(item => item.id !== registrationId);
      setCurrentData(updatedData);
      
      const response = await fetch(`${API_BASE}/api/admin-registration/${registrationId}/finalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const result = await response.json();
        const photoText = result.photo_attached ? " with photo attachment" : "";
        alert(`✅ ${firstName} ${lastName} finalized successfully!\n📧 Email sent${photoText}`);
        
        // Sequential data refresh to prevent race conditions
        // First refresh dashboard stats
        await fetchDashboardStats();
        
        // Then refresh the current pending tab if we're on it
        if (activeTab === 'pending') {
          await fetchPaginatedData('pending', currentPage, true);
        }
        
        // Finally refresh submitted tab (page 1 to show newly submitted)
        await fetchPaginatedData('submitted', 1, true);
        
      } else {
        // Revert optimistic update on failure
        setCurrentData(originalData);
        const errorText = await response.text();
        setError(`Failed to finalize: ${errorText}`);
        alert(`❌ Failed to finalize: ${errorText}`);
      }
      
    } catch (error) {
      // Revert optimistic update on network error
      const originalData = currentData.filter(item => item.id !== registrationId);
      if (originalData.length !== currentData.length) {
        // Need to restore original data
        await fetchPaginatedData('pending', currentPage, true);
      }
      setError(`Network error: ${error.message}`);
      alert(`❌ Network error: ${error.message}`);
    } finally {
      setFinalizingId(null);
    }
  };

  const handleRevertToPending = async (registrationId, firstName, lastName) => {
    try {
      const proceed = window.confirm(`Move ${firstName} ${lastName} back to pending status?\n\nThis will allow you to make corrections and resubmit with a new email notification.`);
      
      if (!proceed) return;
      
      setRevertingId(registrationId);
      setError(null);
      
      // Optimistic UI update - immediately remove from submitted list
      const originalData = [...currentData];
      const updatedData = currentData.filter(item => item.id !== registrationId);
      setCurrentData(updatedData);
      
      const response = await fetch(`${API_BASE}/api/admin-registration/${registrationId}/revert-to-pending`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${firstName} ${lastName} moved back to pending status!\n🔄 You can now make corrections and resubmit.`);
        
        // Sequential data refresh to prevent race conditions
        // First refresh dashboard stats
        await fetchDashboardStats();
        
        // Then refresh the current submitted tab if we're on it
        if (activeTab === 'submitted') {
          await fetchPaginatedData('submitted', currentPage, true);
        }
        
        // Finally refresh pending tab (page 1 to show newly reverted)
        await fetchPaginatedData('pending', 1, true);
        
      } else {
        // Revert optimistic update on failure
        setCurrentData(originalData);
        const errorText = await response.text();
        setError(`Failed to revert to pending: ${errorText}`);
        alert(`❌ Failed to revert: ${errorText}`);
      }
      
    } catch (error) {
      // Revert optimistic update on network error
      const originalData = currentData.filter(item => item.id !== registrationId);
      if (originalData.length !== currentData.length) {
        // Need to restore original data
        await fetchPaginatedData('submitted', currentPage, true);
      }
      setError(`Network error: ${error.message}`);
      alert(`❌ Network error: ${error.message}`);
    } finally {
      setRevertingId(null);
    }
  };

  // Memoized render functions for better performance
  const renderRegistrationItem = useMemo(() => (item, index) => (
    <div key={item.id} className="border rounded-lg p-4 bg-gray-50">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            {item.firstName} {item.lastName}
            {item.disposition && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-semibold">{item.disposition}</span>}
          </h3>
          <div className="text-sm text-gray-600 mt-1">
            <p style={{ whiteSpace: 'nowrap', fontSize: '14px' }}>
              Registration Date: {item.regDate || 'Not provided'}
            </p>
            <p style={{ whiteSpace: 'nowrap', fontSize: '14px' }}>
              Submitted: {new Date(item.timestamp).toLocaleString()}
            </p>
            {item.finalized_at && (
              <p style={{ whiteSpace: 'nowrap', fontSize: '14px' }}>
                Finalized: {new Date(item.finalized_at).toLocaleString()}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-1">ID: {item.id}</p>
          </div>
          
          {/* Lazy loaded photo */}
          {loadedPhotos[item.id] && (
            <div className="mt-4 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Uploaded Photo:</p>
              <img 
                src={loadedPhotos[item.id]} 
                alt="Registration photo"
                className="max-w-xs max-h-48 object-contain border rounded"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </div>
          )}
          
          {!loadedPhotos[item.id] && !loadingPhotos.has(item.id) && (
            <button
              onClick={() => loadPhoto(item.id)}
              className="mt-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Load Photo
            </button>
          )}
          
          {loadingPhotos.has(item.id) && (
            <div className="mt-2 text-sm text-gray-500">Loading photo...</div>
          )}
        </div>
      </div>
      
      {/* Action Buttons - Horizontal layout with intuitive colors */}
      <div className="flex gap-2 mt-4 flex-wrap">
        <button
          onClick={() => {
            sessionStorage.setItem('admin_authenticated', 'true');
            navigate(`/admin-edit/${item.id}`);
          }}
          className="bg-black hover:bg-gray-800 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium flex-1 min-w-[60px]"
        >
          Edit
        </button>
        
        <button
          onClick={() => handleDelete(item.id, item.firstName, item.lastName)}
          disabled={deletingId === item.id}
          className="bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[60px]"
        >
          {deletingId === item.id ? 'Deleting...' : 'Delete'}
        </button>
        
        {activeTab === 'pending' && (
          <button
            onClick={() => handleFinalize(item.id, item.firstName, item.lastName, loadedPhotos[item.id])}
            disabled={finalizingId === item.id}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[70px]"
          >
            {finalizingId === item.id ? 'Submitting...' : 'Submit'}
          </button>
        )}
        
        {activeTab === 'submitted' && (
          <button
            onClick={() => handleRevertToPending(item.id, item.firstName, item.lastName)}
            disabled={revertingId === item.id}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md transition-colors text-xs font-medium disabled:opacity-50 flex-1 min-w-[70px]"
          >
            {revertingId === item.id ? 'Reverting...' : 'Back to Pending'}
          </button>
        )}
      </div>
    </div>
  ), [loadedPhotos, loadingPhotos, deletingId, finalizingId, activeTab]);

  const renderActivityItem = useMemo(() => (item, index) => (
    <div key={item.id} className="border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {item.description}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              item.status === 'upcoming' 
                ? 'bg-blue-100 text-blue-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {item.status === 'upcoming' ? 'Upcoming' : 'Completed'}
            </span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            <p className="font-medium">Client: {item.client_name} {item.client_disposition && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-semibold ml-2">{item.client_disposition}</span>}</p>
            <p>Date: {new Date(item.date).toLocaleDateString()}</p>
            {item.time && <p>Time: {item.time}</p>}
            {item.client_phone && <p>Phone: {item.client_phone}</p>}
            <p className="text-xs text-gray-500 mt-1">Activity ID: {item.id}</p>
          </div>
        </div>
      </div>
      
      <div className="flex gap-2 mt-4">
        <button
          onClick={() => {
            sessionStorage.setItem('admin_authenticated', 'true');
            navigate(`/admin-edit/${item.registration_id}`);
          }}
          className="bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-md transition-colors text-xs font-medium"
        >
          View Client Profile
        </button>
      </div>
    </div>
  ), []);

  // Pagination Component - Mobile Responsive
  const PaginationControls = () => (
    <div className="flex flex-col sm:flex-row items-center justify-between mt-6 px-4 py-3 bg-gray-50 rounded-lg gap-4">
      <div className="flex items-center gap-2 text-sm text-gray-600 text-center sm:text-left">
        <span>
          Showing {((currentPage - 1) * pageSize) + 1} to{' '}
          {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} results
        </span>
      </div>
      
      <div className="flex items-center gap-2 flex-wrap justify-center">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage <= 1 || loading}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
        >
          Previous
        </button>
        
        <div className="flex items-center gap-1 flex-wrap">
          {[...Array(Math.min(5, totalPages))].map((_, i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }
            
            return (
              <button
                key={pageNum}
                onClick={() => handlePageChange(pageNum)}
                disabled={loading}
                className={`px-3 py-1 text-sm rounded-md ${
                  pageNum === currentPage
                    ? 'bg-black text-white'
                    : 'border border-gray-300 hover:bg-gray-100'
                } disabled:opacity-50`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>
        
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= totalPages || loading}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
        >
          Next
        </button>
      </div>
    </div>
  );

  const goBack = () => {
    navigate('/');
  };

  const handleLogout = () => {
    // Clear authentication flags
    sessionStorage.removeItem('admin_authenticated');
    sessionStorage.removeItem('current_user');
    
    // Navigate to home page
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Admin Dashboard</h1>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/admin-menu')}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Admin Menu
            </button>
            <button
              onClick={() => {
                sessionStorage.setItem('admin_authenticated', 'true');
                navigate('/admin-register');
              }}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Register
            </button>
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-2 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Home
            </button>
            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1 px-2 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Tabs */}
          <div className="flex border-b mb-6">
            <button
              onClick={() => setActiveTab('activities')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'activities'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Activities ({dashboardStats.total_activities})
            </button>
            <button
              onClick={() => setActiveTab('pending')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'pending'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Pending ({dashboardStats.pending_registrations})
            </button>
            <button
              onClick={() => setActiveTab('submitted')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'submitted'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Submitted ({dashboardStats.submitted_registrations})
            </button>
          </div>

          {/* Header */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-gray-900">
                {activeTab === 'activities' ? 'Activities' : 'Registrations'}
              </h2>
              {loading && (
                <span className="text-xs text-blue-600 flex items-center gap-1">
                  <svg className="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading...
                </span>
              )}
            </div>
            <button
              onClick={() => fetchPaginatedData(activeTab, currentPage, true)}
              disabled={loading}
              className="bg-gray-100 text-gray-700 py-1 px-3 rounded-md hover:bg-gray-200 transition-colors text-sm disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </>
              )}
            </button>
          </div>

          {/* Search and Filters - Mobile Responsive */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {activeTab === 'activities' ? 'Search Activities' : 'Search by Name'}
                </label>
                <input
                  type="text"
                  placeholder={activeTab === 'activities' ? 'Search description or client' : 'e.g. smith, j'}
                  value={activeTab === 'activities' ? activitySearchTerm : searchName}
                  onChange={(e) => activeTab === 'activities' ? setActivitySearchTerm(e.target.value) : handleNameSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{ height: '40px', minHeight: '40px', maxHeight: '40px' }}
                />
              </div>
              <div className="min-w-0">
                <label className="block text-sm font-medium text-gray-700 mb-1">Search by Date</label>
                <input
                  type="date"
                  value={searchDate}
                  onChange={(e) => handleDateSearch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{ height: '40px', minHeight: '40px', maxHeight: '40px' }}
                />
              </div>
              
              {activeTab === 'activities' ? (
                <div className="min-w-0 md:col-span-2 xl:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    value={activityStatusFilter}
                    onChange={(e) => setActivityStatusFilter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ height: '40px', minHeight: '40px', maxHeight: '40px' }}
                  >
                    <option value="all">All Activities</option>
                    <option value="upcoming">Upcoming</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              ) : (
                <>
                  <div className="min-w-0">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Disposition</label>
                    <select
                      value={searchDisposition}
                      onChange={(e) => handleDispositionSearch(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      style={{ height: '40px', minHeight: '40px', maxHeight: '40px' }}
                    >
                      <option value="">All Dispositions</option>
                      <option value="ACTIVE">ACTIVE</option>
                      <option value="BW RLTS">BW RLTS</option>
                      <option value="CONSULT REQ">CONSULT REQ</option>
                      <option value="DELIVERY">DELIVERY</option>
                      <option value="DISPENSING">DISPENSING</option>
                      <option value="PENDING">PENDING</option>
                      <option value="POCT NEG">POCT NEG</option>
                      <option value="PREVIOUSLY TX">PREVIOUSLY TX</option>
                      <option value="SELF CURED">SELF CURED</option>
                      <option value="SOT">SOT</option>
                    </select>
                  </div>
                  <div className="min-w-0">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Referral Site</label>
                    <select
                      value={searchReferralSite}
                      onChange={(e) => handleReferralSiteSearch(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      style={{ height: '40px', minHeight: '40px', maxHeight: '40px' }}
                    >
                      <option value="">All Sites</option>
                      <option value="Anago">Anago</option>
                      <option value="AIDS Saskatoon">AIDS Saskatoon</option>
                      <option value="Avenue Community Centre for Gender and Sexual Diversity">Avenue Community Centre for Gender and Sexual Diversity</option>
                      <option value="Direction">Direction</option>
                      <option value="Dr K">Dr K</option>
                      <option value="Haven">Haven</option>
                      <option value="Hepatitis">Hepatitis</option>
                      <option value="My420.ca">My420.ca</option>
                      <option value="NEACH">NEACH</option>
                      <option value="Needle Exchange Van">Needle Exchange Van</option>
                      <option value="Nine Circles CHC">Nine Circles CHC</option>
                      <option value="OICHC">OICHC</option>
                      <option value="ORT Program">ORT Program</option>
                      <option value="REACH">REACH</option>
                      <option value="Sheway">Sheway</option>
                      <option value="Sunshine Health Centre">Sunshine Health Centre</option>
                      <option value="Streetworks">Streetworks</option>
                      <option value="SWAP Regina">SWAP Regina</option>
                      <option value="TERF">TERF</option>
                    </select>
                  </div>
                </>
              )}
            </div>
            
            {/* Clear All Filters Button */}
            {(searchName || searchDate || searchDisposition || searchReferralSite || activitySearchTerm || activityStatusFilter !== 'all') && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={clearAllFilters}
                  className="bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors text-sm"
                >
                  Clear All Filters
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Content Area */}
          {loading && currentData.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-600">Loading {activeTab}...</div>
            </div>
          ) : (
            <div>
              {/* No Data Messages */}
              {currentData.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-600">
                    {totalRecords === 0 
                      ? `No ${activeTab} found.`
                      : `No ${activeTab} match your search criteria.`
                    }
                  </p>
                </div>
              )}

              {/* Data Display */}
              {currentData.length > 0 && (
                <>
                  {/* Performance optimized rendering */}
                  <div className="space-y-4">
                    {activeTab === 'activities' 
                      ? currentData.map(renderActivityItem)
                      : currentData.map(renderRegistrationItem)
                    }
                  </div>
                  
                  {/* Pagination Controls */}
                  {totalPages > 1 && <PaginationControls />}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;