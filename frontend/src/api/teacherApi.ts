import axiosClient from "./axiosClient";

export interface Teacher {
  teacher_id: string;
  name: string;
  gender: string;
  subject: string;
  special_notes?: string;
}

const teacherApi = {
  // Get all teachers
  getTeachers: async (): Promise<Teacher[]> => {
    const response = await axiosClient.get("/teachers/");
    return response.data;
  },

  // Get a single teacher by ID
  getTeacher: async (teacherId: string): Promise<Teacher> => {
    const response = await axiosClient.get(`/teachers/${teacherId}/`);
    return response.data;
  },

  // Create a new teacher
  createTeacher: async (data: Omit<Teacher, "teacher_id">): Promise<Teacher> => {
    const response = await axiosClient.post("/teachers/", data);
    return response.data;
  },

  // Update a teacher
  updateTeacher: async (teacherId: string, data: Partial<Teacher>): Promise<Teacher> => {
    const response = await axiosClient.put(`/teachers/${teacherId}/`, data);
    return response.data;
  },

  // Delete a teacher
  deleteTeacher: async (teacherId: string): Promise<void> => {
    await axiosClient.delete(`/teachers/${teacherId}/`);
  },
};

export default teacherApi;
