"use client";
import React, { useState, useRef, ChangeEvent } from "react";
import {
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  Card,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Snackbar,
  Alert,
  AlertColor,
  CardHeader,
} from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { useAuthStore } from "@store/auth-store";
import reportApi from "@/api/reportApi";

const AnalysisReportForm = () => {
  const { control, handleSubmit, reset, setValue, getValues } = useForm({
    defaultValues: {
      rank: 5,
      esr: -0.8,
      rre: 0.5,
      modifiedRRE: 0.35,
      inaccurateEsr: 2.718,
      iterations: 1,
      exportCsv: true,
      method: "default",
      algorithm: "1",
    }
  });
  const dataUser = useAuthStore((state) => state.user);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: AlertColor;
  }>({ open: false, message: "", severity: "success" });

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // Prepare config object without the file reference
      const configValues = { ...values };

      // Add file name to config if a file was selected
      if (selectedFile) {
        configValues.fileName = selectedFile.name;
      }

      const reportData = {
        teacher_id: dataUser?.email || "",
        name: "Analysis Report",
        description: "Generated from Analysis Engine form",
        config: configValues,
      };

      // First, create the report config
      const response = await reportApi.createReportConfig(reportData);
      console.log("Report created:", response);

      // If a file was selected, upload it
      if (selectedFile) {
        try {
          const uploadResponse = await reportApi.uploadFile(response.id, selectedFile);
          console.log("File uploaded:", uploadResponse);
        } catch (uploadError) {
          console.error("Failed to upload file:", uploadError);
          setSnackbar({
            open: true,
            message: "Report configuration created but file upload failed",
            severity: "warning"
          });
          return;
        }
      }

      setSnackbar({
        open: true,
        message: "Report configuration created successfully!",
        severity: "success"
      });
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Failed to create report:", error);
      setSnackbar({
        open: true,
        message: "Failed to create report configuration",
        severity: "error"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Card sx={{ maxWidth: 600, mx: "auto" }}>
        <CardHeader title="Analysis Engine" />
        <CardContent>
          <Box component="form" onSubmit={handleSubmit(onFinish)} noValidate>
            <Box mb={2}>
              <Typography variant="subtitle2" mb={1}>Reference Data File</Typography>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Button
                  variant="outlined"
                  component="label"
                  sx={{ mr: 2 }}
                >
                  Click to Upload
                  <input
                    type="file"
                    hidden
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                  />
                </Button>
                <Typography variant="body2">
                  {selectedFile ? selectedFile.name : "No file selected"}
                </Typography>
              </Box>
            </Box>

            <FormControl fullWidth margin="normal" size="small">
              <InputLabel id="method-label">Calling Method</InputLabel>
              <Controller
                name="method"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    labelId="method-label"
                    label="Calling Method"
                    size="small"
                  >
                    <MenuItem value="default">Default</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </Select>
                )}
              />
            </FormControl>

            <Controller
              name="rank"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Rank"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ min: 1, max: 10, step: 1 }}
                />
              )}
            />

            <Box mt={1} mb={1}>
              <Controller
                name="exportCsv"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={field.value}
                        onChange={field.onChange}
                      />
                    }
                    label="Export CSV"
                  />
                )}
              />
            </Box>

            <Controller
              name="esr"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Standard Deviation ESR (A)"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ step: 0.1 }}
                />
              )}
            />

            <Controller
              name="rre"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Relative Root Error (RRE) (B)"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ step: 0.01 }}
                />
              )}
            />

            <Controller
              name="modifiedRRE"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Modified Lower Rank RRE (C)"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ step: 0.01 }}
                />
              )}
            />

            <Controller
              name="inaccurateEsr"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Inaccurate Standard Deviation ESR (D)"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ step: 0.001 }}
                />
              )}
            />

            <Controller
              name="iterations"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Execution Count"
                  type="number"
                  fullWidth
                  margin="normal"
                  size="small"
                  inputProps={{ min: 1, max: 10, step: 1 }}
                />
              )}
            />

            <FormControl fullWidth margin="normal" size="small">
              <InputLabel id="algorithm-label">Algorithm Mode</InputLabel>
              <Controller
                name="algorithm"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    labelId="algorithm-label"
                    label="Algorithm Mode"
                    size="small"
                  >
                    <MenuItem value="1">MAP</MenuItem>
                    <MenuItem value="2">ML</MenuItem>
                  </Select>
                )}
              />
            </FormControl>

            <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                sx={{ mr: 1 }}
              >
                Start Analysis
              </Button>
              <Button
                variant="outlined"
                onClick={() => {
                  reset();
                  setSelectedFile(null);
                  if (fileInputRef.current) {
                    fileInputRef.current.value = "";
                  }
                }}
              >
                Close
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default AnalysisReportForm;
