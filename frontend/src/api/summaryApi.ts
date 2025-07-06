import axiosClient from "./axiosClient";

export interface StudentSummary {
  student_id: string;
  name: string;
  grade: number;
  class_name: string;
  attendance: {
    present: number;
    absent: number;
    late: number;
  };
  grades: {
    subject: string;
    score: number;
  }[];
  [key: string]: any;
}

const summaryApi = {
  // Get student summary for a teacher
  getStudentSummary: async (teacherId: string): Promise<StudentSummary[]> => {
    const response = await axiosClient.get(`/summary/${teacherId}/`);
    return response.data;
  },

  // Get summary by student ID
  getStudentDetailSummary: async (studentId: string): Promise<StudentSummary> => {
    const response = await axiosClient.get(`/summary/student/${studentId}/`);
    return response.data;
  },
};

export default summaryApi;
