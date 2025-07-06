import axiosClient from "./axiosClient";

export interface ReportConfigCreate {
  teacher_id: string;
  name: string;
  description?: string;
  config: Record<string, any>;
}

export interface ReportConfigOut extends ReportConfigCreate {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ReportResultCreate {
  report_config_id: number;
  status: "pending" | "processing" | "completed" | "failed";
  result_data?: Record<string, any>;
  error_message?: string;
  started_at?: string;
  finished_at?: string;
  notified?: boolean;
  notified_at?: string;
}

export interface ReportResultOut extends ReportResultCreate {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ReportError {
  code: string;
  message: string;
  detail?: string;
}

const reportApi = {
  // Create a new report configuration
  createReportConfig: async (data: ReportConfigCreate): Promise<ReportConfigOut> => {
    const response = await axiosClient.post("/reports", data);
    return response.data;
  },

  // Get all report configurations for a teacher
  getReportConfigs: async (teacherId: string): Promise<ReportConfigOut[]> => {
    const response = await axiosClient.get("/reports", {
      params: { teacher_id: teacherId },
    });
    return response.data;
  },

  // Get a specific report configuration
  getReportConfig: async (reportId: number): Promise<ReportConfigOut> => {
    const response = await axiosClient.get(`/reports/${reportId}`);
    return response.data;
  },

  // Run a report
  runReport: async (reportId: number): Promise<ReportResultOut> => {
    const response = await axiosClient.post(`/reports/${reportId}/run`);
    return response.data;
  },

  // Get all results for a report
  getReportResults: async (reportId: number): Promise<ReportResultOut[]> => {
    const response = await axiosClient.get(`/reports/${reportId}/results`);
    return response.data;
  },

  // Get a specific result
  getReportResult: async (resultId: number): Promise<ReportResultOut> => {
    const response = await axiosClient.get(`/reports/results/${resultId}`);
    return response.data;
  },
  // Notify about a report result
  notifyReportResult: async (resultId: number): Promise<ReportResultOut> => {
    const response = await axiosClient.post(`/reports/${resultId}/notify`);
    return response.data;
  },

  // Upload a file for a report configuration
  uploadFile: async (reportConfigId: number, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('report_config_id', reportConfigId.toString());

    const response = await axiosClient.post("/reports/upload-file", formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all report errors
  getReportErrors: async (): Promise<ReportError[]> => {
    const response = await axiosClient.get("/reports/errors");
    return response.data;
  },
};

export default reportApi;
