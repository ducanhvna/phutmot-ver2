import axios from "axios";
import { API_URL } from "@providers/config";

export interface EmployeeInfo {
  id: number;
  code: string;
  name: string;
  level: number;
  active: boolean;
  user_id: boolean | number;
  birthday: string;
  coach_id: [number, string] | null;
  date_sign: string;
  job_title: string;
  parent_id: [number, string] | null;
  company_id: [number, string] | null;
  work_email: string;
  work_phone: string | boolean;
  workingday: string;
  write_date: string;
  employee_ho: boolean;
  mobile_phone: string;
  department_id: [number, string] | null;
  employee_type: string;
  severance_day: string | boolean;
  personal_email: string;
  working_status: string;
  time_keeping_code: string;
  part_time_company_id: [number, string] | null;
  resource_calendar_id: [number, string] | null;
  part_time_department_id: [number, string] | boolean | null;
  probationary_salary_rate: number;
  probationary_contract_termination_date: string;
}

export interface Employee {
  id: number;
  info: EmployeeInfo;
  total_minutes: number;
  schedulings: AttendanceRecord[]; // Đổi từ attendance sang schedulings
}

export interface AttendanceRecord {
  id: number;
  employee_id: number;
  day: number;
  shift: string;
  start_time: string;
  end_time: string;
  minutes_worked: number;
  check_in: string;
  check_out: string;
  early_leave: number;
  late_arrival: number;
  outside_minutes: number;
  is_complete: boolean;
}

// Hàm lấy danh sách nhân viên từ API backend
export const fetchEmployees = async (token: string, month?: number, year?: number): Promise<Employee[]> => {
  let url = `${API_URL}/hrms/employee_scheduling/`;
  if (month && year) {
    url += `?month=${month}&year=${year}`;
  }
  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data.results;
};

// Hàm lấy thông tin chi tiết theo ID của schedulings từ API backend
export const fetchDetail = async (schedulingId: number, token: string): Promise<AttendanceRecord | null> => {
  // Gọi lại API danh sách, sau đó tìm schedulings theo id (hoặc tạo API riêng nếu cần)
  const employees = await fetchEmployees(token);
  for (const employee of employees) {
    const record = employee.schedulings.find(att => att.id === schedulingId);
    if (record) {
      return record;
    }
  }
  return null;
};
