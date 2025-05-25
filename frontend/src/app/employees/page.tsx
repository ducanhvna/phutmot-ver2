"use client";

import React, { useEffect, useState } from "react";
import { Input, DatePicker, Tabs, Table, Row, Col, Spin } from "antd";
import type { TabsProps } from "antd";
import dayjs from "dayjs";
import { fetchEmployees } from "@providers/data-provider/employee-provider";
import { getAccessTokenFromCookie } from "@/providers/auth-provider/auth-provider.client";

const { Search } = Input;

interface Employee {
  id: number;
  info: any;
  [key: string]: any;
}

export default function EmployeesPage() {
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [month, setMonth] = useState(dayjs().month() + 1);
  const [year, setYear] = useState(dayjs().year());
  const [data, setData] = useState<Employee[]>([]);
  const [companyTabs, setCompanyTabs] = useState<TabsProps["items"]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      let token = getAccessTokenFromCookie();
      if (!token) {
        token = "dumy_token"; // Dummy token for testing
      }
      if (!token) return;
      const res = await fetchEmployees(token, 1, 10000, month, year);
      // Nếu muốn tìm kiếm phía client, filter ở đây
      let filtered = res.results;
      if (keyword) {
        const kw = keyword.toLowerCase();
        filtered = filtered.filter((emp: Employee) =>
          emp.info?.code?.toLowerCase().includes(kw) ||
          emp.info?.name?.toLowerCase().includes(kw) ||
          emp.info?.job_title?.toLowerCase().includes(kw) ||
          emp.info?.work_email?.toLowerCase().includes(kw) ||
          emp.info?.mobile_phone?.toLowerCase().includes(kw) ||
          emp.info?.working_status?.toLowerCase().includes(kw)
        );
      }
      setData(filtered);
    } catch (e) {
      setData([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, [keyword, month, year]);

  useEffect(() => {
    // Group by company
    const companyMap: { [key: string]: Employee[] } = {};
    data.forEach((emp: Employee) => {
      const companyKey = emp.info?.company_id?.[0] || "Khác";
      if (!companyMap[companyKey]) companyMap[companyKey] = [];
      companyMap[companyKey].push(emp);
    });

    // Tạo tab cho mỗi công ty
    const tabs: TabsProps["items"] = Object.values(companyMap).map((emps: Employee[], idx: number) => {
      const companyName = emps[0]?.info?.company_id?.[1] || "Khác";
      // Group by department
      const deptMap: { [key: string]: Employee[] } = {};
      emps.forEach((emp: Employee) => {
        const deptKey = emp.info?.department_id?.[0] || "Khác";
        if (!deptMap[deptKey]) deptMap[deptKey] = [];
        deptMap[deptKey].push(emp);
      });

      return {
        key: String(idx),
        label: companyName,
        children: (
          <>
            {Object.values(deptMap).map((deptEmps: Employee[], didx: number) => (
              <div key={didx} style={{ marginBottom: 32 }}>
                <h3>
                  {deptEmps[0]?.info?.department_id?.[1] || "Phòng ban khác"}
                </h3>
                <Table
                  dataSource={deptEmps}
                  rowKey="id"
                  pagination={false}
                  columns={[
                    { title: "Mã NV", dataIndex: ["info", "code"] },
                    { title: "Tên", dataIndex: ["info", "name"] },
                    { title: "Chức danh", dataIndex: ["info", "job_title"] },
                    { title: "Email", dataIndex: ["info", "work_email"] },
                    { title: "Điện thoại", dataIndex: ["info", "mobile_phone"] },
                    { title: "Trạng thái", dataIndex: ["info", "working_status"] },
                  ]}
                />
              </div>
            ))}
          </>
        ),
      };
    });
    setCompanyTabs(tabs);
  }, [data]);

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col>
          <Search
            placeholder="Tìm kiếm nhân viên"
            allowClear
            onSearch={setKeyword}
            style={{ width: 250 }}
          />
        </Col>
        <Col>
          <DatePicker
            picker="month"
            value={dayjs(`${year}-${month}-01`)}
            onChange={d => {
              if (d) {
                setMonth(d.month() + 1);
                setYear(d.year());
              }
            }}
            format="MM-YYYY"
            style={{ width: 150 }}
          />
        </Col>
      </Row>
      {loading ? (
        <Spin />
      ) : (
        <Tabs items={companyTabs} />
      )}
    </div>
  );
}
