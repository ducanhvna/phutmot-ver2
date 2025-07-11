import axios from 'axios';

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

export async function getAllEmployees(token?: string): Promise<Employee[]> {
  const res = await axios.get<Employee[]>(
    '/api/education/employees',
    token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
  );
  return res.data;
}

export async function getEmployeeById(empId: number, token?: string): Promise<Employee | null> {
  const res = await axios.get<Employee | null>(
    `/api/education/employees/${empId}`,
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