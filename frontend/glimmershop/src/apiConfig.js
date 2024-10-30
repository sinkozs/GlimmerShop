import axios from "axios";
import config from "./config";

const apiClient = axios.create({
  baseURL: config.BACKEND_BASE_URL,
  withCredentials: true,
});

export default apiClient;
