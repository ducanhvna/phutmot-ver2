import axiosClient from "./axiosClient";

export interface AuthLoginParams {
    email?: string;
    username?: string;
    password: string;
    remember?: boolean;
}

export interface AuthLoginResponse {
    user: User
    access_token: string;
    refresh_token: string;
}

export type Role = "admin" | "teacher" | "student";

export interface User {
    name: string;
    email: string;
    roles: Role[];
    avatar: string;
    student_id: null
    teacher_id: string | null;
    username: string | null;
}

export interface RefreshTokenParams {
    refresh_token: string;
}

const authApi = {
    // Login with username/email and password
    login: async (params: AuthLoginParams): Promise<AuthLoginResponse> => {
        const formData = new URLSearchParams();
        formData.append("username", params.email || params.username || "");
        formData.append("password", params.password);

        const response = await axiosClient.post("/auth/token", formData, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        });
        return response.data;
    },

    // Refresh token
    refreshToken: async (params: RefreshTokenParams): Promise<AuthLoginResponse> => {
        const response = await axiosClient.post("/auth/refresh-token", params);
        return response.data;
    },

    // Get current user profile
    getProfile: async (): Promise<any> => {
        const response = await axiosClient.get("/auth/me");
        return response.data;
    },
};

export default authApi;
