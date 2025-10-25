import React, { createContext, useState, useCallback, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import apiClient from "../utils/apiConfig";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

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
          error: "Login failed - Invalid credentials",
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

  const checkAuth = useCallback(async () => {
    setIsCheckingAuth(true);
    try {
      await apiClient.get("/auth/test");
      setIsAuthenticated(true);
    } catch (error) {
      if (
        error.response?.status === 401 ||
        error.response?.status === 403 ||
        !error.response
      ) {
        setIsAuthenticated(false);
        navigate("/", { replace: true });
      }
    } finally {
      setIsCheckingAuth(false);
    }
  }, [navigate, logout]);

  // Check authentication on mount/refresh - but only if not on login page
  useEffect(() => {
    const isLoginPage = location.pathname === "/";

    if (!isLoginPage) {
      checkAuth();
    }
  }, [location.pathname]);

  const value = {
    isAuthenticated,
    isCheckingAuth,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
