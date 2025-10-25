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

      const isLoginAttempt = error.config.url.includes('/auth/login');

      if ((error.response.status === 401 || error.response.status === 403) && !isLoginAttempt) {
          if (logoutHandler) {
              logoutHandler();
          }
          return Promise.reject(error);
      }

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

      return Promise.reject(error);
  }
);

export default apiClient;