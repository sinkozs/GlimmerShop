import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    console.log("isAuthenticated changed:", isAuthenticated);
  }, [isAuthenticated]);

  const checkAuth = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/auth/test", {
        withCredentials: true,
      });
      console.log("checkAuth...");
      console.log(response);
      setIsAuthenticated(true);
    } catch (error) {
      setIsAuthenticated(false);
    }
  };

  const login = () => {
    console.log("calling login");
    setIsAuthenticated(true);
    console.log("login isAuth");
    console.log(isAuthenticated);
  };

  const logout = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/auth/logout",
        {},
        {
          withCredentials: true,
        }
      );
      setIsAuthenticated(false); // Only set to false if the logout is successful
      console.log(response.data); // Optional: Log the response for debugging
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
