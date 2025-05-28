"use client";
import React from "react";
import { Card, Table, Typography, Tag } from "antd";

// Demo dữ liệu báo cáo
const reports = [
  { id: 1, name: "Báo cáo chấm công tháng 5/2025", type: "Chấm công", created: "2025-05-25", status: "Đã duyệt" },
  { id: 2, name: "Báo cáo nhân sự quý 1/2025", type: "Nhân sự", created: "2025-04-10", status: "Chờ duyệt" },
  { id: 3, name: "Báo cáo lương tháng 4/2025", type: "Lương", created: "2025-04-05", status: "Đã duyệt" },
];

const columns = [
  { title: "Tên báo cáo", dataIndex: "name", key: "name" },
  { title: "Loại báo cáo", dataIndex: "type", key: "type" },
  { title: "Ngày tạo", dataIndex: "created", key: "created" },
  {
    title: "Trạng thái",
    dataIndex: "status",
    key: "status",
    render: (status: string) => (
      <Tag color={status === "Đã duyệt" ? "green" : "orange"}>{status}</Tag>
    ),
  },
];

export default function ReportsPage() {
  return (
    <Card title={<Typography.Title level={3}>Danh sách báo cáo</Typography.Title>}>
      <Table columns={columns} dataSource={reports} rowKey="id" pagination={false} />
    </Card>
  );
}
