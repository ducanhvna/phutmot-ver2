import axios, { AxiosInstance } from "axios";
import Cookies from "js-cookie";
import { refreshToken } from "@/providers/auth-provider/auth-provider.client";

const axiosClient: AxiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

// Request interceptor:auto attached access_token vào header
axiosClient.interceptors.request.use(
    (config) => {
        const token = Cookies.get("access_token");
        if (token) {
            config.headers = config.headers || {};
            config.headers["Authorization"] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor: auto reload token if 401 Unauthorized
axiosClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (
            error.response &&
            error.response.status === 401 &&
            !originalRequest._retry
        ) {
            originalRequest._retry = true;
            const result = await refreshToken();
            if (result.success) {
                const token = Cookies.get("access_token");
                if (token) {
                    originalRequest.headers["Authorization"] = `Bearer ${token}`;
                }
                return axiosClient(originalRequest);
            }
        }
        return Promise.reject(error);
    }
);

export default axiosClient;
