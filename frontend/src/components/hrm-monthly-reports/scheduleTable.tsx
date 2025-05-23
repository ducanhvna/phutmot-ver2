import React from "react";
import { Table, Modal, Spin, Button } from "antd";
import { AttendanceRecord, Employee, Scheduling } from "@/providers/data-provider/employee-provider";
import AttendanceCell from "./AttendanceCell";
import ModalDetail from "./modalDetail";
import ToDoTask from "./ToDoTask";

interface ScheduleTableProps {
  employees: Employee[];
  month: number;
  year: number;
  total: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

const ScheduleTable: React.FC<ScheduleTableProps> = ({ employees, month, year, total, currentPage, pageSize, onPageChange }) => {
  const daysInMonth = new Date(year, month, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const [selectedDetail, setSelectedDetail] = React.useState<AttendanceRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleCellClick = (attendanceId: number) => {
    setIsModalOpen(true);
    setIsLoading(true);
    // Find the record in the employees prop (search all schedulings)
    let found: AttendanceRecord | null = null;
    for (const employee of employees) {
      for (const scheduling of employee.schedulings) {
        const record = scheduling.scheduling_records.find((att: AttendanceRecord) => att.id === attendanceId);
        if (record) {
          found = record;
          break;
        }
      }
      if (found) break;
    }
    setSelectedDetail(found);
    setIsLoading(false);
  };

  // Hàm lấy ngày (số) từ chuỗi date dạng YYYY-MM-DD
  const getDayFromDateStr = (dateStr: string) => {
    if (!dateStr) return null;
    const parts = dateStr.split("-");
    return parts.length === 3 ? parseInt(parts[2], 10) : null;
  };

  // Flatten employees to rows: mỗi scheduling là một hàng
  const rows = employees.flatMap((employee: Employee) =>
    employee.schedulings.map((scheduling: Scheduling) => ({
      key: `${employee.id}_${scheduling.id}`,
      employee_code: employee.info.code,
      name: employee.info.name,
      total_minutes: employee.total_minutes,
      scheduling_id: scheduling.id,
      // ...other scheduling fields nếu cần
      ...Object.fromEntries(days.map((day) => {
        const attendanceRecord = scheduling.scheduling_records.find((att: AttendanceRecord) => {
          // Sử dụng trường date (YYYY-MM-DD) thay vì day
          return getDayFromDateStr(att.date) === day;
        });
        return [day, attendanceRecord ?? null];
      }))
    }))
  );

  return (
    <>
      <Table
        bordered
        dataSource={rows}
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
        pagination={{
          total,
          current: currentPage,
          pageSize,
          showSizeChanger: false,
          onChange: onPageChange,
        }}
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
