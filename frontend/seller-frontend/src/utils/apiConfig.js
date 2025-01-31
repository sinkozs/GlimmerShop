import axios from "axios";
import config from "../config";

let logoutHandler = null;

export const setLogoutHandler = (handler) => {
    logoutHandler = handler;
};

const apiClient = axios.create({
    baseURL: config.BACKEND_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true
});

apiClient.interceptors.response.use(
  response => response,
  error => {
      if (!error.response) {
          console.error('Network error: Unable to reach server');
          return Promise.reject(error);
      }

      const isAuthenticated = localStorage.getItem('seller_id');
      
      if (isAuthenticated) {
          switch (error.response.status) {
              case 401:
                  // Unauthorized - log out
                  if (!window.location.pathname.includes('login')) {
                      if (logoutHandler) logoutHandler();
                  }
                  break;
              case 403:
                  // Forbidden - log out
                  if (logoutHandler) logoutHandler();
                  break;
              case 404:
                  console.error('Resource not found');
                  break;
              case 500:
                  console.error('Server error');
                  break;
              default:
                  console.error('An error occurred:', error.response.data);
          }
      }

      return Promise.reject(error);
  }
);

export default apiClient;