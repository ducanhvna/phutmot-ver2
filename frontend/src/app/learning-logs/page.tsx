"use client";

import React from "react";
import {
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const columns = [
  { title: "ID", dataIndex: "id", key: "id" },
  { title: "学習者名 (Tên học viên)", dataIndex: "name", key: "name" },
  { title: "コース (Khóa học)", dataIndex: "course", key: "course" },
  { title: "登録日 (Ngày đăng ký)", dataIndex: "registrationDate", key: "registrationDate" },
  { title: "進捗 (Tiến độ)", dataIndex: "progress", key: "progress" },
  { title: "スコア (Điểm số)", dataIndex: "score", key: "score" },
  { title: "ステータス (Trạng thái)", dataIndex: "status", key: "status" },
  { title: "メモ (Ghi chú)", dataIndex: "notes", key: "notes" },
  { title: "学習時間 (Thời gian học)", dataIndex: "studyHours", key: "studyHours" },
  { title: "ファイルアップロード (Tải lên tài liệu)", dataIndex: "upload", key: "upload" },
];

const dummyData = Array.from({ length: 10 }).map((_, i) => ({
  id: i + 1,
  name: `学習者 ${i + 1}`,
  course: `コース ${i + 1}`,
  registrationDate: `2025-05-${String(i + 10).padStart(2, "0")}`,
  progress: `${Math.floor(Math.random() * 100)}%`,
  score: `${Math.floor(Math.random() * 100)}/100`,
  status: i % 2 === 0 ? "完了 (Hoàn thành)" : "学習中 (Đang học)",
  notes: `メモ ${i + 1}`,
  studyHours: `${Math.floor(Math.random() * 50)} 時間`,
}));

export default function LearningLogsPage() {
  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h4">学習ログUL+登録確認 (Tải lên nhật ký học tập + Xác nhận đăng ký)</Typography>
      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>学習者名 (Tên học viên)</TableCell>
              <TableCell>コース (Khóa học)</TableCell>
              <TableCell>登録日 (Ngày đăng ký)</TableCell>
              <TableCell>進捗 (Tiến độ)</TableCell>
              <TableCell>スコア (Điểm số)</TableCell>
              <TableCell>ステータス (Trạng thái)</TableCell>
              <TableCell>メモ (Ghi chú)</TableCell>
              <TableCell>学習時間 (Thời gian học)</TableCell>
              <TableCell>ファイルアップロード (Tải lên tài liệu)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dummyData.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.id}</TableCell>
                <TableCell>{row.name}</TableCell>
                <TableCell>{row.course}</TableCell>
                <TableCell>{row.registrationDate}</TableCell>
                <TableCell>{row.progress}</TableCell>
                <TableCell>{row.score}</TableCell>
                <TableCell>{row.status}</TableCell>
                <TableCell>{row.notes}</TableCell>
                <TableCell>{row.studyHours}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    size="small"
                  >
                    アップロード (Tải lên)
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}
