"use client";

import type { AuthProvider } from "@refinedev/core";
import Cookies from "js-cookie";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/api";

export const authProviderClient: AuthProvider = {
  login: async ({ email, username, password, remember }) => {
    try {
      const data = await authApi.login({ email, username, password, remember });
      Cookies.set("auth", JSON.stringify(data.user), {
        expires: 30,
        path: "/",
      });
      Cookies.set("access_token", data.access_token, {
        expires: 30,
        path: "/",
      });
      Cookies.set("refresh_token", data.refresh_token, {
        expires: 30,
        path: "/",
      });

      if (typeof window !== "undefined") {
        const { setAuth } = useAuthStore.getState();
        setAuth({
          user: data.user,
          access_token: data.access_token,
          refresh_token: data.refresh_token,
        });

        if (data.user.roles.includes("admin")) {
          window.location.href = "/admin";
        }
        if (data.user.roles.includes("teacher")) {
          window.location.href = "/top-teacher";
        }
        if (data.user.roles.includes("student")) {
          window.location.href = "/top-student";
        }
      }

      return {
        success: true,
        redirectTo: `/top-${data.user.roles[0]}`,
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "LoginError",
          message: "Something went wrong",
        },
      };
    }
  },
  logout: async () => {
    Cookies.remove("auth", { path: "/" });
    Cookies.remove("access_token", { path: "/" });
    Cookies.remove("refresh_token", { path: "/" });
    if (typeof window !== "undefined") {
      const { clearAuth } = useAuthStore.getState();
      clearAuth();
    }
    return {
      success: true,
      redirectTo: "/login",
    };
  },
  check: async () => {
    const auth = Cookies.get("auth");
    if (auth) {
      return {
        authenticated: true,
      };
    }

    return {
      authenticated: false,
      logout: true,
      redirectTo: "/login",
    };
  },
  getPermissions: async () => {
    const auth = Cookies.get("auth");
    if (auth) {
      const parsedUser = JSON.parse(auth);
      return parsedUser.roles;
    }
    return null;
  },
  getIdentity: async () => {
    const auth = Cookies.get("auth");
    if (auth) {
      const parsedUser = JSON.parse(auth);
      return parsedUser;
    }
    return null;
  },
  onError: async (error) => {
    if (error.response?.status === 401) {
      return {
        logout: true,
      };
    }

    return { error };
  },
};

/**
 * Gọi API refresh-token, cập nhật lại state và cookies nếu thành công
 */
export const refreshToken = async () => {
  try {
    const refresh_token = Cookies.get("refresh_token");
    if (!refresh_token) throw new Error("No refresh token");
    const data = await authApi.refreshToken({ refresh_token });
    // Lưu lại vào cookies
    Cookies.set("auth", JSON.stringify(data.user), { expires: 30, path: "/" });
    Cookies.set("access_token", data.access_token, { expires: 30, path: "/" });
    Cookies.set("refresh_token", data.refresh_token, { expires: 30, path: "/" });
    // Lưu vào global state (Zustand)
    if (typeof window !== "undefined") {
      const { setAuth } = useAuthStore.getState();
      setAuth({
        user: data.user,
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      });
    }
    return { success: true };
  } catch (error) {
    if (typeof window !== "undefined") {
      const { clearAuth } = useAuthStore.getState();
      clearAuth();
    }
    Cookies.remove("auth", { path: "/" });
    Cookies.remove("access_token", { path: "/" });
    Cookies.remove("refresh_token", { path: "/" });
    return { success: false, error: error instanceof Error ? error.message : "Unknown error" };
  }
};
