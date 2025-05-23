import React from "react";
import { Table, Modal, Spin, Button } from "antd";
import { AttendanceRecord, Employee } from "@/providers/data-provider/employee-provider";
import AttendanceCell from "./AttendanceCell";
import ModalDetail from "./modalDetail";
import ToDoTask from "./ToDoTask";

interface ScheduleTableProps {
  employees: Employee[];
  month: number;
  year: number;
}

const ScheduleTable: React.FC<ScheduleTableProps> = ({ employees, month, year }) => {
  const daysInMonth = new Date(year, month, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const [selectedDetail, setSelectedDetail] = React.useState<AttendanceRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  // Token extraction logic for detail fetch
  const getTokenFromCookie = () => {
    if (typeof document === "undefined") return "";
    const authCookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("auth="));
    if (!authCookie) return "";
    try {
      const authData = JSON.parse(decodeURIComponent(authCookie.split("=")[1]));
      return authData.access_token || "";
    } catch {
      return "";
    }
  };

  const handleCellClick = (attendanceId: number) => {
    setIsModalOpen(true);
    setIsLoading(true);
    // Find the record in the employees prop
    let found: AttendanceRecord | null = null;
    for (const employee of employees) {
      const record = employee.schedulings.find((att: AttendanceRecord) => att.id === attendanceId);
      if (record) {
        found = record;
        break;
      }
    }
    setSelectedDetail(found);
    setIsLoading(false);
  };

  return (
    <>
      <Table
        bordered
        dataSource={employees.map((employee: Employee) => ({
          key: employee.id,
          employee_code: employee.info.code,
          attendance: employee.schedulings,
          total_minutes: employee.total_minutes,
          name: employee.info.name,
          ...Object.fromEntries(days.map((day) => {
            const attendanceRecord = employee.schedulings.find((att: AttendanceRecord) => att.day === day);
            return [day, attendanceRecord ?? null];
          }))
        }))}
        columns={[
          { title: "Mã NV", dataIndex: "employee_code", key: "employee_code", fixed: "left" },
          { title: "Nhân viên", dataIndex: "name", key: "name", fixed: "left" },
          { title: "SUM", dataIndex: "total_minutes", key: "total_minutes", fixed: "left" },
          ...days.map((day) => ({
            title: `${day}`,
            dataIndex: `${day}`,
            key: `${day}`,
            render: (record: AttendanceRecord | null) => {
              return record ? (
                <AttendanceCell record={record} onClick={() => handleCellClick(record.id)} />
              ) : "-";
            },
          }))
        ]}
        scroll={{ x: "max-content", y: 800 }}
      />
      <Modal
        title="Chi tiết điểm danh"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={isExpanded ? 1050 : 800}
      >
        {isLoading ? (
          <Spin size="large" />
        ) : selectedDetail ?
          <div style={{ display: "flex", alignItems: "start", gap: "20px", marginTop: "20px" }}>
            <div style={{ display: "block" }}>
              {isExpanded && <ToDoTask />}
            </div>
            <Button type="default" onClick={() => setIsExpanded(!isExpanded)} style={{ height: "30px" }}>
              {isExpanded ? "Thu gọn" : "Công việc"}
            </Button>
            <div style={{ display: "block" }}>
              <ModalDetail eventDetail={selectedDetail} />
            </div>
          </div>
          : (
          <p style={{ color: "red" }}>Không tìm thấy dữ liệu cho ID này.</p>
        )}
      </Modal>
    </>
  );
};

export default ScheduleTable;
