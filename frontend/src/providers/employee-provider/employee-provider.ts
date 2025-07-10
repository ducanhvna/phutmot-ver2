import axios from 'axios';

const API_BASE_URL = '/api/education'; // Điều chỉnh endpoint nếu backend khác

export interface Employee {
  id: number;
  name: string;
  work_email?: string;
  work_phone?: string;
  job_title?: string;
  department_id?: any;
  user_id?: any;
  // Bổ sung các trường khác nếu cần
}

export async function getAllEmployees(): Promise<Employee[]> {
  const res = await axios.get<Employee[]>(`${API_BASE_URL}/employees`);
  return res.data;
}

export async function getEmployeeById(empId: number): Promise<Employee | null> {
  const res = await axios.get<Employee | null>(`${API_BASE_URL}/employees/${empId}`);
  return res.data;
}

export async function getEmployeeByUserId(userId: number): Promise<Employee | null> {
  const res = await axios.get<Employee | null>(`${API_BASE_URL}/employees/by-user/${userId}`);
  return res.data;
}