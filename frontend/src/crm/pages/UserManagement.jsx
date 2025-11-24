import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserServices } from "../../services/userServices";
import PasswordInput from "../ui/PasswordInput";
import ConfirmModal from "../components/ConfirmModal";
import { useUsers } from "../../context/UserContext";
import toast from "react-hot-toast";

function EditUser({
  editingUser,
  handleUpdateUser,
  handleAddUser,
  handleInputChange,
  formData,
  loading,
  handlePermissionChange,
  resetForm,
}) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        {editingUser ? "Edit User" : "Add New User"}
      </h2>

      <form onSubmit={editingUser ? handleUpdateUser : handleAddUser}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ height: "40px" }}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name *
            </label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ height: "40px" }}
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
              style={{ height: "40px" }}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone Number *
            </label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              placeholder="(XXX) XXX-XXXX"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ height: "40px" }}
              required
            />
          </div>
        </div>

        <PasswordInput
          formData={formData}
          handleInputChange={handleInputChange}
          required={editingUser ? false : true}
        />

        {/* Role Selection Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            User Role
          </label>
          <div class="grid grid-cols-2 gap-4">
            {["admin", "standard", "guest", "limited"].map((roleOption) => (
              <div key={roleOption} className="flex items-center">
                <input
                  type="radio"
                  id={`role-${roleOption}`}
                  name="role"
                  value={roleOption}
                  checked={formData.role === roleOption}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  // required
                />
                <label
                  htmlFor={`role-${roleOption}`}
                  className="ml-2 block text-sm text-gray-700 capitalize"
                >
                  {roleOption}
                </label>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Choose the overall role for this user
          </p>
        </div>

        {/* Tab Permissions Section */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Tab Access Permissions
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              "Client",
              "Assessments",
              "Medication",
              "Dispensing",
              "Notes",
              "Activities",
              "Interactions",
              "Attachments",
            ].map((tab) => (
              <div key={tab} className="flex items-center">
                <input
                  type="checkbox"
                  id={`permission-${tab}`}
                  checked={formData.permissions.includes(tab.toLowerCase())}
                  onChange={() => handlePermissionChange(tab.toLowerCase())}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`permission-${tab}`}
                  className="ml-2 block text-sm text-gray-700"
                >
                  {tab}
                </label>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Select which tabs this user can access
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800 transition-colors text-sm font-medium disabled:opacity-50"
          >
            {loading
              ? "Saving..."
              : editingUser
                ? "Update User"
                : "Create User"}
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
  );
}

function UserList({ handleEditUser, handleDeleteUser }) {
  const { users, fetchUsers, loading } = useUsers();

  function capitalizeFirstLetter(word = "") {
    return word.charAt(0).toUpperCase() + word.slice(1);
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">
          Users ({users.length})
        </h2>
        <button
          onClick={fetchUsers}
          disabled={loading}
          className="bg-gray-100 text-gray-700 py-1 px-3 rounded-md hover:bg-gray-200 transition-colors text-sm disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh"}
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
              <p className="text-gray-600">
                No users found. Create your first user to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {users.map((user) => (
                <div key={user.id} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {capitalizeFirstLetter(user.first_name)}{" "}
                        {capitalizeFirstLetter(user.last_name)}
                      </h3>
                      <div className="text-sm text-gray-600 mt-1 space-y-1">
                        <p>
                          <strong>Email:</strong> {user.email}
                        </p>
                        <p>
                          <strong>Phone:</strong> {user.phone_number}
                        </p>
                        <p>
                          <strong>Tab Access:</strong>{" "}
                          {Array.isArray(user.permissions) &&
                          user.permissions.length > 0
                            ? user.permissions
                                .map((tab) => capitalizeFirstLetter(tab))
                                .join(", ")
                            : "No access"}
                        </p>
                        <p>
                          <strong>Created:</strong>{" "}
                          {new Date(user.created_at).toLocaleString()}
                        </p>
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
                      onClick={() => handleDeleteUser(user.id)}
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
    </div>
  );
}

const UserManagement = () => {
  const navigate = useNavigate();
  const { fetchUsers } = useUsers();
  const [loading, setLoading] = useState(false);
  const [showAddUser, setShowAddUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [user, setUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteUserId, setDeleteUserId] = useState(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    password: "",
    role: "",
    permissions: [],
  });

  const resetForm = () => {
    setFormData({
      first_name: "",
      last_name: "",
      email: "",
      phone_number: "",
      password: "",
      role: "",
      permissions: [],
    });
    setEditingUser(null);
    setShowAddUser(false);
  };

  const validateAddForm = () => {
    if (!formData.first_name) {
      toast.error("First Name required");
      return false;
    }

    if (!formData.last_name) {
      toast.error("Last Name required");
      return false;
    }

    if (!formData.email) {
      toast.error("Please fill in all required fields");
      return false;
    }

    if (!formData.phone_number) {
      toast.error("Phone number required");
      return false;
    }

    if (!formData.password) {
      toast.error("Password required");
      return false;
    }
    if (!formData.role) {
      toast.error("Role required");
      return false;
    }

    return true;
  };

  const validateEditForm = () => {
    if (!formData.first_name) {
      toast.error("First Name required");
      return false;
    }

    if (!formData.last_name) {
      toast.error("Last Name required");
      return false;
    }

    if (!formData.email) {
      toast.error("Please fill in all required fields");
      return false;
    }

    if (!formData.phone_number) {
      toast.error("Phone number required");
      return false;
    }

    return true;
  };

  // Handle add user
  const handleAddUser = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (validateAddForm()) {
      const response = await UserServices.create_user(formData);

      if (response.success) {
        resetForm();
        fetchUsers();
        toast.success("User created successfully");
      } else {
        if (response.status === 400 || response.status === 409) {
          toast.error(response.message || "Failed to create users.");
        } else {
          toast.error("Failed to create user. Please try again.");
        }
      }
    }
    setLoading(false);
  };

  // Handle update user
  const handleUpdateUser = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (validateEditForm()) {
      const response = await UserServices.update_user(editingUser.id, formData);

      if (response.success) {
        resetForm();
        fetchUsers();
        toast.success("User updated successfully");
      } else {
        if (response.status === 400 || response.status === 409) {
          toast.error(response.message || "Failed to create users.");
        } else {
          toast.error("Failed to create user. Please try again.");
        }
      }
    }
    setLoading(false);
  };

  // Handle delete user
  const deleteUser = async () => {
    setLoading(true);

    const response = await UserServices.delete_user(deleteUserId);

    if (response.success) {
      resetForm();
      fetchUsers();
      toast.success("User deleted successfully");
    } else {
      if (response.status === 400 || response.status === 409) {
        toast.error(response.message || "Failed to create users.");
      } else {
        toast.error("Failed to create user. Please try again.");
      }
    }

    setLoading(false);
  };

  const handleDeleteUser = async (id) => {
    setDeleteUserId(id);
    setShowDeleteConfirm(true);
  };

  // Handle edit user
  const handleEditUser = (user) => {
    setFormData({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone_number: user.phone_number,
      password: "",
      role: user.role,
      permissions: user.permissions || [],
    });
    setEditingUser(user);
    setUser(user);
    setShowAddUser(true);
    window.scrollTo(0, 0);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle permissions checkbox changes
  const handlePermissionChange = (tab) => {
    setFormData((prev) => {
      const hasTab = prev.permissions.includes(tab);

      return {
        ...prev,
        permissions: hasTab
          ? prev.permissions.filter((p) => p !== tab) // remove if already selected
          : [...prev.permissions, tab], // add if not
      };
    });
  };

  const goBack = () => {
    navigate("/admin-menu");
  };

  return (
    <div className="bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            User Management
          </h1>
          <div className="flex gap-2">
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-2 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Admin Menu
            </button>
            <button
              onClick={() => setShowAddUser(!showAddUser)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              {showAddUser ? "Cancel" : "Add User"}
            </button>
          </div>
        </div>

        {showDeleteConfirm && (
          <ConfirmModal
            message={"Confirm you would like to delete user"}
            subMessage={"This action cannot be undone"}
            confirm={deleteUser}
            setShowConfirm={setShowDeleteConfirm}
          />
        )}

        {/* Add/Edit User Form */}
        {showAddUser && (
          <EditUser
            editingUser={editingUser}
            handleUpdateUser={handleUpdateUser}
            handlePermissionChange={handlePermissionChange}
            handleAddUser={handleAddUser}
            handleInputChange={handleInputChange}
            formData={formData}
            loading={loading}
            resetForm={resetForm}
          />
        )}

        {/* Users List */}
        <UserList
          handleEditUser={handleEditUser}
          handleDeleteUser={handleDeleteUser}
        />
      </div>
    </div>
  );
};

export default UserManagement;
