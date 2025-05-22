import React from "react";
import { AttendanceRecord } from "@/providers/data-provider/employee-provider";
import { Tag, Tooltip, Card } from "antd";

const AttendanceCell: React.FC<{ record: AttendanceRecord; onClick: () => void }> = ({ record, onClick }) => {
  return (
    <Tooltip title={`Số phút làm việc: ${record.minutes_worked}`} placement="top">
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
            backgroundColor: record.is_complete ? "#a0e7a0" : record.late_arrival > 0 || record.early_leave > 0 ? "#f5c08d" : "#f8d7da",
            padding: "5px",
            borderRadius: "5px",
          }}
        >
          {record.start_time} - {record.end_time}
        </div>

        {/* Dòng 2 - Nền trong suốt */}
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", backgroundColor: "transparent", padding: "5px" }}>
          <span>{record.minutes_worked} phút</span>
          <span style={{ flex: 2 }}>{record.check_in} → {record.check_out}</span>
        </div>

        {/* Dòng 3 - Nền trong suốt, với tag màu sắc */}
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", backgroundColor: "transparent", padding: "5px" }}>
          <Tag color={record.late_arrival > 0 ? "orange" : "default"}>{record.late_arrival} phút muộn</Tag>
          <Tag color={record.outside_minutes > 0 ? "gold" : "default"}>{record.outside_minutes} phút ngoài</Tag>
          <Tag color={record.early_leave > 0 ? "orange" : "default"}>{record.early_leave} phút sớm</Tag>
        </div>
      </Card>
    </Tooltip>
  );
};

export default AttendanceCell;
