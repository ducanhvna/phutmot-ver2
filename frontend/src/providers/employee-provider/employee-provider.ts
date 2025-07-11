import axios from 'axios';

export interface UserDetail {
  id: number;
  name: string;
  login?: string;
  email?: string;
  company_id?: any;
  active?: boolean;
}

export interface Employee {
  id: number;
  name: string;
  work_email?: string;
  work_phone?: string;
  job_title?: string;
  department_id?: any;
  user_id?: any;
  user_detail?: UserDetail | null;
  // Bổ sung các trường khác nếu cần
}

export async function getAllEmployees(token?: string): Promise<Employee[]> {
  try {
    const baseUrl = 'http://localhost:8979'; // Hardcoded for now
    const res = await axios.get<Employee[]>(
      `${baseUrl}/api/odoo/employees`,
      token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
    );
    return res.data;
  } catch (error) {
    console.error('Error fetching employees:', error);
    return [];
  }
}

export async function getEmployeeById(empId: number, token?: string): Promise<Employee | null> {
  const baseUrl = 'http://localhost:8979';
  const res = await axios.get<Employee | null>(
    `${baseUrl}/api/odoo/employees/${empId}`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
  );
  return res.data;
}

export async function getEmployeeByUserId(userId: number, token?: string): Promise<Employee | null> {
  const res = await axios.get<Employee | null>(
    `/api/education/employees/by-user/${userId}`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
  );
  return res.data;
}