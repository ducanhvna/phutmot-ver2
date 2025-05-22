import React, { useState } from "react";
import { Table, Modal, Spin, Button } from "antd";
import { mockEmployees, fetchDetail, AttendanceRecord } from "@/providers/data-provider/employee-provider";
import AttendanceCell from "./AttendanceCell";
import ModalDetail from "./modalDetail"; // ✅ Import ModalDetail trực tiếp
import ToDoTask from "./ToDoTask"; // ✅ Import ModalDetail trực tiếp

const ScheduleTable: React.FC<{ month: number; year: number }> = ({ month, year }) => {
  const daysInMonth = new Date(year, month, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  // State lưu dữ liệu chi tiết
  const [selectedDetail, setSelectedDetail] = useState<AttendanceRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleCellClick = (attendanceId: number) => {
    setIsModalOpen(true);
    setIsLoading(true);

    var data = fetchDetail(attendanceId);
    setSelectedDetail(data as AttendanceRecord);
    setIsLoading(false);
  };

  return (
    <>
      <Table
        bordered
        dataSource={mockEmployees.map((employee) => ({
          key: employee.id,
          employee_code: employee.employee_code,
          attendance: employee.attendance,
          total_minutes: employee.total_minutes,
          name: employee.name,
          ...Object.fromEntries(days.map((day) => {
            const attendanceRecord = employee.attendance.find(att => att.day === day);
            return [day, attendanceRecord ?? null]; // Trả về toàn bộ object `attendanceRecord`
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

      {/* Modal hiển thị thông tin chi tiết */}
      <Modal
        title="Chi tiết điểm danh"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={isExpanded ? 1050 : 800} // ✅ Điều chỉnh độ rộng theo trạng thái
      >
        {isLoading ? (
          <Spin size="large" />
        ) : selectedDetail ?
          <div style={{ display: "flex", alignItems: "start", gap: "20px", marginTop: "20px" }}>
            {/* Todo Task sẽ hiển thị bên trái */}
            <div style={{ display: "block" }}>
              {isExpanded && <ToDoTask />}
            </div>
            {/* Nút mở rộng / thu gọn */}
            <Button type="default" onClick={() => setIsExpanded(!isExpanded)} style={{ height: "30px" }}>
              {isExpanded ? "Thu gọn" : "Công việc"}
            </Button>
            <div style={{ display: "block" }}>
              {/* Form chi tiết chấm công bên phải */}
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
