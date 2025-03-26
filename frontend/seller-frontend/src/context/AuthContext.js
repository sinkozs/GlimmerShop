import React, { createContext, useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../utils/apiConfig";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    // Prevent multiple concurrent auth checks
    if (isCheckingAuth) return;
    
    setIsCheckingAuth(true);
    try {
      await apiClient.get("/auth/test");
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        setIsAuthenticated(false);
        navigate("/login", { replace: true });
      }
    } finally {
      setIsCheckingAuth(false);
    }
  }, [navigate, isCheckingAuth]);

  const login = useCallback(
    async (sellerId) => {
      try {
        if (sellerId) {
          setIsAuthenticated(true);
          navigate(`/seller/${sellerId}`, { state: { sellerId } });
          return { success: true };
        }
        return {
          success: false,
          error: "Login failed - Invalid credentials"
        };
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
    } catch (error) {
      console.error("Logout failed:", error.response?.data || error.message);
    } finally {
      setIsAuthenticated(false);
      navigate("/", { replace: true });
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