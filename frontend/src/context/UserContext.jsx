import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserServices } from "../services/userServices";

const UsersContext = createContext();

export const useUsers = () => useContext(UsersContext);

export function UsersProvider({ children }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);

  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);

    const response = await UserServices.get_users();

    if (response.success) {
      setUsers(response.data);
    } else {
      if (response.status === 400 || response.status === 409) {
        setError(response.message || "Invalid credentials.");
      } else {
        setError("Login failed. Please try again.");
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <UsersContext.Provider
      value={{
        users,
        fetchUsers,
        loading,
      }}
    >
      {children}
    </UsersContext.Provider>
  );
}
