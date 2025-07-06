"use client";
import React from "react";
import { useRouter } from "next/navigation";
import {
  Typography,
  Box,
  Paper,
  Button,
  Alert,
  IconButton,
  Tooltip,
} from "@mui/material";
import { Show } from "@refinedev/mui";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import ErrorIcon from "@mui/icons-material/Error";
import NoteIcon from "@mui/icons-material/Note";
import DateRangeIcon from "@mui/icons-material/DateRange";
import SharedTable from "@components/shared-table";

export default function LearningDataEntryPage() {
  // Sample data for the learning data history
  const learningData = [
    {
      id: 1,
      registrationDate: "2025/6/3 14:30",
      educationalSystem: "ドリルパーク",
      year: "2025",
      grade: "1年",
      subject: "数学・数A",
      targetPeriod: "05/26～06/03",
      recordCount: 233,
      registrar: "山田太郎",
    },
    {
      id: 2,
      registrationDate: "2025/6/2 10:15",
      educationalSystem: "スタディサプリⅠ型",
      year: "2025",
      grade: "2年",
      subject: "英語",
      targetPeriod: "04/10～05/26",
      recordCount: 1020,
      registrar: "佐藤花子",
    },
    {
      id: 3,
      registrationDate: "2025/5/30 16:45",
      educationalSystem: "ドリルパーク",
      year: "2025",
      grade: "3年",
      subject: "社会・世界史",
      targetPeriod: "05/01～05/29",
      recordCount: 40,
      registrar: "鈴木昌平",
    },
    {
      id: 4,
      registrationDate: "2025/5/28 09:20",
      educationalSystem: "スタディサプリⅠ型",
      year: "2025",
      grade: "1年, 2年",
      subject: "理科",
      targetPeriod: "05/01～05/27",
      recordCount: 350,
      registrar: "田中誠",
    },
    {
      id: 5,
      registrationDate: "2025/5/25 13:10",
      educationalSystem: "ドリルパーク",
      year: "2025",
      grade: "3年",
      subject: "国語",
      targetPeriod: "04/20～05/24",
      recordCount: 125,
      registrar: "山田太郎",
    },
    {
      id: 6,
      registrationDate: "2025/5/20 11:30",
      educationalSystem: "スタディサプリⅠ型",
      year: "2025",
      grade: "2年",
      subject: "英語",
      targetPeriod: "04/01～05/19",
      recordCount: 890,
      registrar: "佐藤花子",
    },
    {
      id: 7,
      registrationDate: "2025/5/18 15:45",
      educationalSystem: "ドリルパーク",
      year: "2025",
      grade: "1年",
      subject: "数学・数A",
      targetPeriod: "04/15～05/17",
      recordCount: 210,
      registrar: "鈴木昌平",
    },
  ];

  // Function to handle delete action
  const handleDelete = (id: number) => {
    console.log(`Delete item with ID: ${id}`);
    // Implement delete functionality
  };

  // Function to handle new learning data registration
  const router = useRouter();
  
  const handleNewRegistration = () => {
    router.push("/learning-data-entry/create");
  };

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          学習データ登録履歴
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      {/* Main content container */}
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          gap: 3,
        }}
      >
        {/* Left section - Main content */}
        <Box sx={{ flex: 1 }}>
          {/* Action button */}
          <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 3 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleNewRegistration}
              sx={{
                backgroundColor: "var(--color-green)",
                "&:hover": {
                  backgroundColor: "var(--color-green)",
                  opacity: 0.9,
                },
              }}
            >
              新規学習データ登録
            </Button>
          </Box>

          {/* Data table */}
          <Paper
            elevation={2}
            sx={{ borderRadius: "10px", overflow: "hidden", mb: 3 }}
          >
            <SharedTable
              dataSource={learningData}
              themeColor="var(--color-green)"
              columns={[
                {
                  title: "登録日時",
                  dataIndex: "registrationDate",
                  key: "registrationDate",
                },
                {
                  title: "教材システム",
                  dataIndex: "educationalSystem",
                  key: "educationalSystem",
                },
                {
                  title: "年度",
                  dataIndex: "year",
                  key: "year",
                },
                {
                  title: "学年",
                  dataIndex: "grade",
                  key: "grade",
                },
                {
                  title: "教科・科目",
                  dataIndex: "subject",
                  key: "subject",
                },
                {
                  title: "対象期間",
                  dataIndex: "targetPeriod",
                  key: "targetPeriod",
                  render: (text, record) => (
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <DateRangeIcon
                        fontSize="small"
                        sx={{ marginRight: 1, color: "var(--color-blue)" }}
                      />
                      {text}
                    </Box>
                  ),
                },
                {
                  title: "レコード数",
                  dataIndex: "recordCount",
                  key: "recordCount",
                },
                {
                  title: "登録者",
                  dataIndex: "registrar",
                  key: "registrar",
                },
                {
                  title: "操作",
                  key: "action",
                  render: (_, record) => (
                    <Tooltip title="削除">
                      <IconButton
                        onClick={() => handleDelete(record.id)}
                        sx={{ color: "var(--color-red)" }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  ),
                },
              ]}
            />
          </Paper>
        </Box>
      </Box>
    </Show>
  );
}
