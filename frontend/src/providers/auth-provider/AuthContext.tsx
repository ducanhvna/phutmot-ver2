"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { getAccessTokenFromCookie } from "@/providers/auth-provider/auth-provider.client";

interface AuthContextType {
  token: string | null;
  setToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType>({ token: null, setToken: () => {} });

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(getAccessTokenFromCookie());
  }, []);

  return (
    <AuthContext.Provider value={{ token, setToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
