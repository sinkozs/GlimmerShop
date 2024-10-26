import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import config from "../config";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
  }, [isAuthenticated]);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${config.BACKEND_BASE_URL}/auth/test`, {
        withCredentials: true,
      });
      setIsAuthenticated(true);
    } catch (error) {
      setIsAuthenticated(false);
    }
  };

  const login = () => {
    setIsAuthenticated(true);
  };

  const logout = async () => {
    try {
      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/auth/logout`,
        {},
        {
          withCredentials: true,
        }
      );
      setIsAuthenticated(false);
    } catch (error) {
      console.error(
        "Logout failed:",
        error.response ? error.response.data : error
      );
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
