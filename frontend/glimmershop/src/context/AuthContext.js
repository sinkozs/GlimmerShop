import React, { createContext, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../utils/apiConfig";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    try {
      const response = await apiClient.get("/auth/test");
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        setIsAuthenticated(false);
        navigate("/login");
      }
    }
  }, [navigate]);

  
  const login = useCallback(
    async (sellerId) => {
      try {
        setIsAuthenticated(true);
        if (sellerId) {
          navigate(`/seller/${sellerId}`, { state: { sellerId } });
        }
        return { success: true };
      } catch (error) {
        setIsAuthenticated(false);
        return {
          success: false,
          error: error.message || "Login failed",
        };
      }
    },
    [navigate]
  );

  const logout = useCallback(async () => {
    try {
      await apiClient.post("/auth/logout");
      setIsAuthenticated(false);
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Logout failed:", error.response?.data || error.message);
      setIsAuthenticated(false);
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const value = {
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
