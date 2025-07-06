import { User } from "@api/authApi";
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface AuthState {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  setAuth: (data: { user: User; access_token: string; refresh_token: string }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      setAuth: ({ user, access_token, refresh_token }) =>
        set({ user, access_token, refresh_token }),
      clearAuth: () => {
        console.log("Clearing auth state");
        return set({ user: null, access_token: null, refresh_token: null });
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
