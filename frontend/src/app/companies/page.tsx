"use client";
import React, { useEffect, useState } from "react";
import { Card, Table, Typography, Spin, Button } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useAuth } from "@/providers/auth-provider/AuthContext";
import { fetchCompanies, CompanyInfo } from "@/providers/data-provider/company-provider";
import { useRouter } from "next/navigation";

const columns: ColumnsType<CompanyInfo> = [
  { title: "ID", dataIndex: "id", key: "id" },
  { title: "Tên công ty", dataIndex: "name", key: "name" },
  { title: "MIS ID", dataIndex: "mis_id", key: "mis_id" },
  { title: "Là HO", dataIndex: "is_ho", key: "is_ho", render: (v) => (v ? "✔️" : "") },
  { title: "Ngày cập nhật", dataIndex: "write_date", key: "write_date" },
];

const CompaniesPage = () => {
  const { token } = useAuth();
  const [data, setData] = useState<CompanyInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const companies = await fetchCompanies(token || undefined);
      setData(companies);
      setLoading(false);
    };
    fetchData();
    // eslint-disable-next-line
  }, [token]);

  return (
    <Card
      title={<Typography.Title level={3}>Danh sách công ty</Typography.Title>}
      extra={
        <Button type="primary" onClick={() => router.push("/companies/create")}>
          Tạo công ty
        </Button>
      }
    >
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          pagination={false}
        />
      </Spin>
    </Card>
  );
};

export default CompaniesPage;
