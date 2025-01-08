import React, { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../utils/apiConfig";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  // Periodically check for authentication status to handle session expiration
  useEffect(() => {
    const interval = setInterval(checkAuth, 20 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const checkAuth = async () => {
    try {
      await apiClient.get("/auth/test");
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response?.status === 403) {
        setIsAuthenticated(false);
        handleLogout();
      }
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate("/login");
  };

  const login = () => {
    setIsAuthenticated(true);
  };

  const logout = async () => {
    try {
      await apiClient.post("/auth/logout", {});
      setIsAuthenticated(false);
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error.response?.data || error.message);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
