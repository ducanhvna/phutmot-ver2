import React from "react";
import { AttendanceRecord } from "@/providers/data-provider/employee-provider";
import { Tag, Tooltip, Card } from "antd";

// Helper: tính trạng thái hoàn thành (is_complete) cho AttendanceRecord
function isAttendanceComplete(record: AttendanceRecord): boolean {
  return record.total_work_time < record.actual_total_work_time;
}

// Helper: tính outside_minutes cho AttendanceRecord
function getOutsideMinutes(record: AttendanceRecord): number {
  return Math.round((record.total_shift_work_time * 480) - record.attendance_late - record.leave_early);
}

const AttendanceCell: React.FC<{ record: AttendanceRecord; onClick: () => void }> = ({ record, onClick }) => {
  return (
    <Tooltip title={`Số phút làm việc: ${record.total_work_time}`} placement="top">
      <Card
        hoverable
        onClick={onClick}
        style={{
          padding: "10px",
          borderRadius: "5px",
          textAlign: "center",
          cursor: "pointer",
          fontSize: "14px",
        }}
      >
        {/* Dòng 1 - Màu nền dựa trên trạng thái */}
        <div
          style={{
            fontWeight: "bold",
            color: "#333",
            backgroundColor: isAttendanceComplete(record)
              ? "#a0e7a0"
              : record.attendance_late > 0 || record.leave_early > 0
              ? "#f5c08d"
              : "#f8d7da",
            padding: "5px",
            borderRadius: "5px",
          }}
        >
          {record.shift_start} - {record.shift_end}
        </div>

        {/* Dòng 2 - Nền trong suốt */}
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", backgroundColor: "transparent", padding: "5px" }}>
          <span>{record.total_work_time} phút</span>
          <span style={{ flex: 2 }}>{record.attendance_attempt_1 ? '✓' : ''} → {record.last_attendance_attempt ? '✓' : ''}</span>
        </div>

        {/* Dòng 3 - Nền trong suốt, với tag màu sắc */}
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", backgroundColor: "transparent", padding: "5px" }}>
          <Tag color={record.attendance_late > 0 ? "orange" : "default"}>{record.attendance_late} phút muộn</Tag>
          <Tag color={getOutsideMinutes(record) > 0 ? "gold" : "default"}>{getOutsideMinutes(record)} phút ngoài</Tag>
          <Tag color={record.leave_early > 0 ? "orange" : "default"}>{record.leave_early} phút sớm</Tag>
        </div>
      </Card>
    </Tooltip>
  );
};

export default AttendanceCell;
