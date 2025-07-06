import axiosClient from "./axiosClient";

export interface Student {
  student_id: string;
  name: string;
  gender: string;
  grade: number;
  class_name: string;
  special_notes?: string;
}

const studentApi = {
  // Get all students
  getStudents: async (): Promise<Student[]> => {
    const response = await axiosClient.get("/students/");
    return response.data;
  },

  // Get a single student by ID
  getStudent: async (studentId: string): Promise<Student> => {
    const response = await axiosClient.get(`/students/${studentId}/`);
    return response.data;
  },

  // Create a new student
  createStudent: async (data: Omit<Student, "student_id">): Promise<Student> => {
    const response = await axiosClient.post("/students/", data);
    return response.data;
  },

  // Update a student
  updateStudent: async (studentId: string, data: Partial<Student>): Promise<Student> => {
    const response = await axiosClient.put(`/students/${studentId}/`, data);
    return response.data;
  },

  // Delete a student
  deleteStudent: async (studentId: string): Promise<void> => {
    await axiosClient.delete(`/students/${studentId}/`);
  },
};

export default studentApi;
