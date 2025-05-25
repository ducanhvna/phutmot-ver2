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

export interface AttendanceRecord {
  id: number;
  date: string; // YYYY-MM-DD
  locked: boolean;
  company: string;
  kid_time: number;
  rest_end: number;
  ot_normal: number;
  shift_end: number;
  department: string;
  ot_holiday: number;
  rest_shift: boolean;
  rest_start: number;
  shift_name: string;
  write_date: string;
  leave_early: number;
  night_shift: boolean;
  shift_start: number;
  split_shift: boolean;
  employee_code: string;
  employee_name: string;
  attendance_late: number;
  total_work_time: number;
  total_attendance: number;
  amount_al_reserve: number;
  amount_cl_reserve: number;
  time_keeping_code: string;
  additional_company: boolean;
  attendance_inout_1: boolean;
  attendance_inout_2: boolean;
  attendance_inout_3: boolean;
  attendance_inout_4: boolean;
  attendance_inout_5: boolean;
  attendance_inout_6: boolean;
  attendance_inout_7: boolean;
  attendance_inout_8: boolean;
  attendance_inout_9: boolean;
  night_hours_normal: number;
  attendance_inout_10: boolean;
  attendance_inout_11: boolean;
  attendance_inout_12: boolean;
  attendance_inout_13: boolean;
  attendance_inout_14: boolean;
  attendance_inout_15: boolean;
  night_hours_holiday: number;
  probation_wage_rate: number;
  attendance_attempt_1: boolean;
  attendance_attempt_2: boolean;
  attendance_attempt_3: boolean;
  attendance_attempt_4: boolean;
  attendance_attempt_5: boolean;
  attendance_attempt_6: boolean;
  attendance_attempt_7: boolean;
  attendance_attempt_8: boolean;
  attendance_attempt_9: boolean;
  standard_working_day: number;
  attendance_attempt_10: boolean;
  attendance_attempt_11: boolean;
  attendance_attempt_12: boolean;
  attendance_attempt_13: boolean;
  attendance_attempt_14: boolean;
  attendance_attempt_15: boolean;
  attendance_inout_last: boolean;
  missing_checkin_break: boolean;
  total_shift_work_time: number;
  actual_total_work_time: number;
  last_attendance_attempt: boolean;
  minutes_working_reduced: number;
  minute_worked_day_holiday: number;
  probation_completion_wage: boolean;
}

export interface Scheduling {
  id: number;
  employee_code: string;
  scheduling_records: AttendanceRecord[];
  // Thêm các trường khác nếu cần
}

export interface Employee {
  id: number;
  info: EmployeeInfo;
  total_minutes: number;
  schedulings: Scheduling[];
}

// Hàm lấy danh sách nhân viên (không scheduling)
export const fetchEmployees = async (
  token: string,
  page?: number,
  pageSize?: number,
  month?: number,
  year?: number
): Promise<{ results: Employee[]; count: number; next: string | null; previous: string | null }> => {
  let url = `${API_URL}/hrms/employees/?`;
  const params = [];
  if (page) params.push(`page=${page}`);
  if (pageSize) params.push(`page_size=${pageSize}`);
  if (month) params.push(`month=${month}`);
  if (year) params.push(`year=${year}`);
  url += params.join("&");
  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// Hàm lấy danh sách nhân viên kèm scheduling (cho page report)
export const fetchEmployeesWithScheduling = async (
  token: string,
  page?: number,
  pageSize?: number,
  month?: number,
  year?: number
): Promise<{ results: Employee[]; count: number; next: string | null; previous: string | null }> => {
  let url = `${API_URL}/hrms/employee_scheduling/?`;
  const params = [];
  if (page) params.push(`page=${page}`);
  if (pageSize) params.push(`page_size=${pageSize}`);
  if (month) params.push(`month=${month}`);
  if (year) params.push(`year=${year}`);
  url += params.join("&");
  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// Hàm lấy thông tin chi tiết theo ID của schedulings từ API backend
export const fetchDetail = async (schedulingId: number, token: string): Promise<AttendanceRecord | null> => {
  // Gọi lại API danh sách, sau đó tìm schedulings theo id (hoặc tạo API riêng nếu cần)
  const data = await fetchEmployees(token);
  const employees = data.results;
  for (const employee of employees) {
    const record = employee.schedulings.find((sched: Scheduling) =>
      sched.scheduling_records.find((att: AttendanceRecord) => att.id === schedulingId)
    );
    if (record) {
      return record.scheduling_records.find((att: AttendanceRecord) => att.id === schedulingId) || null;
    }
  }
  return null;
};
