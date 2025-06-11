import { createContext, useContext, useState, useEffect } from "react";
import ApiService from "../services/api";

// Create the authentication context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);  // Function to check if user is authenticated
  const checkAuthStatus = async () => {
    try {
      // Check if the user is already logged in
      const response = await ApiService.getCurrentUser();
      
      if (response.data) {
        setUser(response.data);
      } else {
        setUser(null);
      }
    } catch (err) {
      // 401 or 403 are expected if user is not logged in or not authorized
      if (err.response && err.response.status !== 401 && err.response.status !== 403) {
        console.error("Auth check failed:", err);
        setError("Authentication failed. Please try again.");
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Function to log in
  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await ApiService.login(username, password);
      
      if (response.data) {
        setUser(response.data);
        return { success: true };
      }
    } catch (err) {
      console.error("Login failed:", err);
      setError(err.response?.data?.detail || "Login failed. Please try again.");
      return { success: false, error: err.response?.data?.detail || "Login failed" };
    } finally {
      setLoading(false);
    }
  };
  // Function to log out
  const logout = async () => {
    try {
      setLoading(true);
      await ApiService.logout();
      // Clear user state no matter what
      setUser(null);
      
      // Clear any cookies that might be related to authentication
      document.cookie.split(";").forEach((cookie) => {
        const [name] = cookie.trim().split("=");
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      
      return { success: true };
    } catch (err) {
      console.error("Logout failed:", err);
      // Even if the API call fails, we should still clear the local state
      setUser(null);
      setError("Logout operation encountered an issue, but you've been logged out locally.");
      return { success: true }; // Return success anyway so UI redirects
    } finally {
      setLoading(false);
    }
  };

  // Check auth status when component mounts
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Value to be provided by the context
  const value = {
    user,
    loading,
    error,
    login,
    logout,
    checkAuthStatus
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthContext;
