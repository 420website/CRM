import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { IoLogOutOutline } from "react-icons/io5";

const AdminMenu = () => {
  const navigate = useNavigate();
  const { userRole, userPermissions, logout } = useAuth();

  const goBack = () => {
    navigate("/");
  };

  const handleLogout = async () => {
    try {
      logout();
    } catch (error) {
      setError("Logout error:", error);
    }
  };

  return (
    <div className="flex-grow flex flex-col bg-gray-50 flex items-center justify-center m-4">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Admin Menu
            </h1>
            <p className="text-gray-600">Choose an option to continue:</p>
          </div>

          {/* Dashboard  */}
          <div className="space-y-6">
            {userRole !== "guest" && (
              <button
                onClick={() => navigate("/admin-dashboard")}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: "#000000" }}
                onMouseEnter={(e) =>
                  (e.target.style.backgroundColor = "#1f2937")
                }
                onMouseLeave={(e) =>
                  (e.target.style.backgroundColor = "#000000")
                }
              >
                📊 Dashboard
              </button>
            )}

            {/* Registration  */}
            {userPermissions.includes("client") && userRole !== "guest" && (
              <button
                onClick={() => navigate("/admin-register")}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: "#000000" }}
                onMouseEnter={(e) =>
                  (e.target.style.backgroundColor = "#1f2937")
                }
                onMouseLeave={(e) =>
                  (e.target.style.backgroundColor = "#000000")
                }
              >
                📝 Registration
              </button>
            )}

            {/* Analytics  */}
            <button
              onClick={() => navigate("/admin-analytics")}
              className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
              style={{ backgroundColor: "#000000" }}
              onMouseEnter={(e) => (e.target.style.backgroundColor = "#1f2937")}
              onMouseLeave={(e) => (e.target.style.backgroundColor = "#000000")}
            >
              <span className="text-lg">🤖</span>
              Analytics
            </button>

            {/* Users */}
            {userRole === "admin" && (
              <button
                onClick={() => navigate("/admin-users")}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors"
                style={{ backgroundColor: "#000000" }}
                onMouseEnter={(e) =>
                  (e.target.style.backgroundColor = "#1f2937")
                }
                onMouseLeave={(e) =>
                  (e.target.style.backgroundColor = "#000000")
                }
              >
                👥 Users
              </button>
            )}
            {/* Logout for guests */}
            {userRole === "guest" && (
              <button
                onClick={handleLogout}
                className="w-full py-4 px-6 rounded-lg text-lg font-medium flex items-center justify-center gap-3 text-white transition-colors bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors  "
              >
                <IoLogOutOutline />
                Logout
              </button>
            )}
          </div>

          {/* Back  */}
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
