"use client";

import { useLogin } from "@refinedev/core";
import { useState } from "react";
import {
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Box,
  InputAdornment,
} from "@mui/material";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import type { AuthPageProps } from "@refinedev/core";
import Image from "next/image";

export const AuthPage = (props: AuthPageProps) => {
  const { mutate: login, isLoading } = useLogin();
  const [error, setError] = useState<string | null>(null);
  const [formValues, setFormValues] = useState({
    email: "teacher02",
    password: "pass456",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    login(
      { email: formValues.email, password: formValues.password },
      {
        onError: (error: any) => {
          setError(error?.message || "Login failed");
        },
      }
    );
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
  return (
    <Box
      sx={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
      }}
    >
      <Card
        sx={{
          width: 400,
          boxShadow: "0 8px 24px rgba(0,0,0,0.1)",
          borderRadius: 2,
          overflow: "hidden",
          padding: 2,
        }}
      >
        <CardContent>
          <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
            <Image width={225} height={90} src="/images/logo.png" alt="Logo" />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              name="email"
              value={formValues.email}
              onChange={handleChange}
              fullWidth
              margin="normal"
              label="Email"
              variant="outlined"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonOutlineIcon sx={{ color: "rgba(0,0,0,.25)" }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              name="password"
              value={formValues.password}
              onChange={handleChange}
              fullWidth
              margin="normal"
              label="Password"
              type="password"
              variant="outlined"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockOutlinedIcon sx={{ color: "rgba(0,0,0,.25)" }} />
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                type="submit"
                disabled={isLoading}
                sx={{
                  borderRadius: 1,
                  backgroundColor: "#17a098",
                  "&:hover": {
                    backgroundColor: "#128d85",
                  },
                }}
              >
                {isLoading ? "Logging in..." : "Login"}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
