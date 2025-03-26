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
      const isLoginAttempt = error.config.url.includes('/auth/login');

      if (isAuthenticated && !isLoginAttempt) {
          switch (error.response.status) {
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