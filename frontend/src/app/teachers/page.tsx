"use client";
import React, { useEffect, useState } from "react";
import { Typography, CircularProgress } from "@mui/material";
import SharedTable, { SharedTableColumn } from "@components/shared-table";

export default function TeacherListPage() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/teachers/`)
      .then((res) => res.json())
      .then((data) => {
        setTeachers(Array.isArray(data) ? data : []);
        setLoading(false);
      });
  }, []);

  const columns: SharedTableColumn[] = [
    { title: "教員番号", dataIndex: "teacher_id", key: "teacher_id" },
    { title: "氏名", dataIndex: "name", key: "name" },
    { title: "性別", dataIndex: "gender", key: "gender" },
    { title: "担当科目", dataIndex: "subject", key: "subject" },
    { title: "特記事項", dataIndex: "special_notes", key: "special_notes" },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Typography variant="h3">教員一覧</Typography>
      {loading ? (
        <CircularProgress />
      ) : (
        <SharedTable
          dataSource={teachers}
          columns={columns}
        />
      )}
    </div>
  );
}
