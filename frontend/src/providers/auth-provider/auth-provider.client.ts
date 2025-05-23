"use client";

import { API_URL } from "@providers/config";
import type { AuthProvider } from "@refinedev/core";
import Cookies from "js-cookie";
import axios from 'axios';

const mockUsers = [
  {
    name: "John Doe",
    email: "johndoe@mail.com",
    roles: ["admin"],
    avatar: "https://i.pravatar.cc/150?img=1",
  },
  {
    name: "Jane Doe",
    email: "janedoe@mail.com",
    roles: ["editor"],
    avatar: "https://i.pravatar.cc/150?img=1",
  },
];

// Hàm lấy access_token an toàn từ cookie "auth"
export const getAccessTokenFromCookie = (): string => {
  const auth = Cookies.get("auth");
  if (!auth) return "";
  try {
    const parsed = JSON.parse(auth);
    return parsed.access_token || "";
  } catch {
    return "";
  }
};

export const authProviderClient: AuthProvider = {
  login: async ({ email, username, password, remember }) => {
    try {
      const response = await axios.post(`${API_URL}/login/`,{ username, password }, { withCredentials: true });

      if (response.data.access_token) {
        // const user = mockUsers.find((u) => u.email === email);
        const user = response.data.user; // Assuming the user data is returned in the response
        if (user) {
          // Đảm bảo access_token luôn là string
          const authData = {
            ...user,
            access_token: String(response.data.access_token),
          };

          Cookies.set("auth", JSON.stringify(authData), {
            expires: 30, // 30 days
            path: "/",
          });

          return {
            success: true,
            redirectTo: "/",
          };
        }
      }

      return {
        success: false,
        error: {
          name: "LoginError",
          message: "Invalid username or password",
        },
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "LoginError",
          message: "Failed to get token",
        },
      };
    }
  },
  // login: async ({ email, username, password, remember }) => {
  //   // Suppose we actually send a request to the back end here.
  //   const user = mockUsers[0];

  //   if (user) {
  //     Cookies.set("auth", JSON.stringify(user), {
  //       expires: 30, // 30 days
  //       path: "/",
  //     });
  //     return {
  //       success: true,
  //       redirectTo: "/",
  //     };
  //   }

  //   return {
  //     success: false,
  //     error: {
  //       name: "LoginError",
  //       message: "Invalid username or password",
  //     },
  //   };
  // },
  logout: async () => {
    Cookies.remove("auth", { path: "/" });
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
