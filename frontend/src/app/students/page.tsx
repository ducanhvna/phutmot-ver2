"use client";
import React, { useEffect, useState } from "react";
import { Typography, CircularProgress } from "@mui/material";
import SharedTable, { SharedTableColumn } from "@components/shared-table";
import { studentApi } from "@api";

export default function StudentListPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentApi
      .getStudents()
      .then((data) => setStudents(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false));
  }, []);

  const columns: SharedTableColumn[] = [
    { title: "学籍番号", dataIndex: "student_id", key: "student_id" },
    { title: "氏名", dataIndex: "name", key: "name" },
    { title: "性別", dataIndex: "gender", key: "gender" },
    { title: "クラス", dataIndex: "class_name", key: "class_name" },
    { title: "特記事項", dataIndex: "special_notes", key: "special_notes" },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Typography variant="h3">生徒一覧</Typography>
      {loading ? (
        <CircularProgress />
      ) : (
        <SharedTable
          dataSource={students}
          columns={columns}
        />
      )}
    </div>
  );
}
