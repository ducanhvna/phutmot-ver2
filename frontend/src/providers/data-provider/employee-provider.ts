import { faker } from "@faker-js/faker";

export interface Employee {
  id: number;
  employee_code: string;
  name: string;
  total_minutes: number;
  attendance: AttendanceRecord[];
}

export interface AttendanceRecord {
  id: number; 
  employee_id: number;
  day: number;
  shift: string;
  start_time: string; // 🟢 Thêm giờ bắt đầu
  end_time: string; // 🟢 Thêm giờ kết thúc
  minutes_worked: number;
  check_in: string; // 🟢 Thời gian vào thực tế
  check_out: string; // 🟢 Thời gian ra thực tế
  early_leave: number; // 🟠 Số phút về sớm
  late_arrival: number; // 🟠 Số phút đi muộn
  outside_minutes: number; // 🟡 Thời gian ra ngoài
  is_complete: boolean;
}

// Biến global để đảm bảo ID không trùng
let currentAttendanceId = 1;

// ✅ Cập nhật dữ liệu giả lập
export const generateEmployees = (daysInMonth: number): Employee[] => {
  return Array.from({ length: 40 }, (_, i) => ({
    id: i + 1,
    employee_code: faker.string.numeric(6),
    name: faker.person.fullName(),
    total_minutes: faker.number.int({ min: 4800, max: 9600 }),
    attendance: Array.from({ length: daysInMonth }, (_, day) => ({
      id: currentAttendanceId++, 
      employee_id: i + 1,
      day: day + 1,
      shift: faker.helpers.arrayElement(["Ca sáng", "Ca chiều", "Ca tối"]),
      start_time: faker.helpers.arrayElement(["08:00", "12:00"]),
      end_time: faker.helpers.arrayElement(["17:00", "20:00"]),
      minutes_worked: faker.number.int({ min: 240, max: 480 }),
      check_in: faker.helpers.arrayElement(["07:55", "08:30", "09:00"]),
      check_out: faker.helpers.arrayElement(["16:30", "17:15", "18:00"]),
      early_leave: faker.number.int({ min: 0, max: 30 }),
      late_arrival: faker.number.int({ min: 0, max: 60 }),
      outside_minutes: faker.number.int({ min: 0, max: 120 }),
      is_complete: faker.datatype.boolean(),
    })),
  }));
};

// Dữ liệu giả lập danh sách nhân viên
export const mockEmployees = generateEmployees(new Date(2025, 5, 0).getDate());

// Hàm lấy thông tin chi tiết theo ID của `attendance`
export const fetchDetail = (attendanceId: number) => {
  for (const employee of mockEmployees) {
    const record = employee.attendance.find(att => att.id === attendanceId);
    if (record) {
      return record;
    }
  }
  return null;
};

export default mockEmployees;
