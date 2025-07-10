"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tooltip,
  Divider,
  Breadcrumbs,
  Link,
} from "@mui/material";
import SharedTable, { SharedTableColumn } from "@/components/shared-table";
import { Show } from "@refinedev/mui";
import DescriptionIcon from "@mui/icons-material/Description";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import VisibilityIcon from "@mui/icons-material/Visibility";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { useRouter, useParams } from "next/navigation";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import { useBack } from "@refinedev/core";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

// Mock test data
const testData = {
  id: "1",
  name: "1学期末考査 数学",
  year: "2025",
  grade: "2年",
  term: "1学期期末テスト",
  subject: "数学",
  testDate: "2025/7/19",
};

// Mock student data
const studentData = [
  {
    id: "1",
    grade: "2",
    classRoom: "1",
    number: "1",
    name: "明智光秀",
    score: 90,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "2",
    grade: "2",
    classRoom: "1",
    number: "2",
    name: "伊能忠敬",
    score: 72,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "3",
    grade: "2",
    classRoom: "1",
    number: "3",
    name: "上杉謙信",
    score: 84,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "4",
    grade: "2",
    classRoom: "1",
    number: "4",
    name: "豊臣秀吉",
    score: 95,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "5",
    grade: "2",
    classRoom: "1",
    number: "5",
    name: "武田信玄",
    score: 88,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "6",
    grade: "2",
    classRoom: "1",
    number: "6",
    name: "織田信長",
    score: 92,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "7",
    grade: "2",
    classRoom: "2",
    number: "1",
    name: "徳川家康",
    score: 89,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "8",
    grade: "2",
    classRoom: "2",
    number: "2",
    name: "足利義満",
    score: 75,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "9",
    grade: "2",
    classRoom: "2",
    number: "3",
    name: "北条政子",
    score: 82,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "10",
    grade: "2",
    classRoom: "2",
    number: "4",
    name: "源頼朝",
    score: 78,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "11",
    grade: "3",
    classRoom: "1",
    number: "1",
    name: "平清盛",
    score: 88,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
  {
    id: "12",
    grade: "3",
    classRoom: "1",
    number: "2",
    name: "本多忠勝",
    score: 79,
    hasAnswerSheet: true,
    hasIndividualSheet: true,
  },
];

const TestReviewDetailPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const testId = params.id as string;

  // State for filters
  const [selectedGrade, setSelectedGrade] = useState<string>("2");
  const [selectedClass, setSelectedClass] = useState<string>("1");

  // Get available grades and classes
  const grades = Array.from(
    new Set(studentData.map((student) => student.grade))
  );
  const classes = Array.from(
    new Set(
      studentData
        .filter((student) => student.grade === selectedGrade)
        .map((student) => student.classRoom)
    )
  );

  // Filter students based on selected grade and class
  const filteredStudents = studentData.filter(
    (student) =>
      student.grade === selectedGrade && student.classRoom === selectedClass
  );

  // Handlers for opening answer sheets and individual sheets
  const handleViewAnswerSheet = (studentId: string) => {
    console.log(`Opening answer sheet for student: ${studentId}`);
    // In a real app, this would open the answer sheet in a modal or new page
    alert(`Opening answer sheet for student ID: ${studentId}`);
  };

  // Handlers for bulk downloads
  const handleBulkAnswerSheetDownload = () => {
    console.log("Downloading all answer sheets");
    alert("Downloading all answer sheets for the selected class");
  };

  const handleBulkIndividualSheetDownload = () => {
    console.log("Downloading all individual sheets");
    alert("Downloading all individual sheets for the selected class");
  };

  const BackButton = () => {
    const goBack = useBack();
    return (
      <IconButton onClick={goBack}>
        <ArrowBackIcon />
      </IconButton>
    );
  };

  // Define columns for SharedTable component
  const columns: SharedTableColumn[] = [
    {
      title: "学年",
      dataIndex: "grade",
      key: "grade",
      width: 80,
    },
    {
      title: "組",
      dataIndex: "classRoom",
      key: "classRoom",
      width: 80,
    },
    {
      title: "番",
      dataIndex: "number",
      key: "number",
      width: 80,
    },
    {
      title: "氏名",
      dataIndex: "name",
      key: "name",
      width: 150,
    },
    {
      title: "得点",
      dataIndex: "score",
      key: "score",
      width: 80,
    },
    {
      title: "答案",
      key: "answerSheet",
      width: 80,
      render: (_, student) =>
        student.hasAnswerSheet ? (
          <Tooltip title="答案表示">
            <IconButton
              size="small"
              color="primary"
              onClick={() => handleViewAnswerSheet(student.id)}
              sx={{ color: "var(--color-blue)" }}
            >
              <VisibilityIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <Typography variant="body2" color="text.secondary">
            未提出
          </Typography>
        ),
    },
    {
      title: "個票",
      key: "individualSheet",
      width: 80,
      render: (_, student) =>
        student.hasIndividualSheet ? (
          <Tooltip title="個票表示">
            <IconButton
              size="small"
              color="primary"
              onClick={() =>
                router.push(`/tests-review/score-student/${student.id}`)
              }
              sx={{ color: "var(--color-green)" }}
            >
              <ContentCopyIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <Typography variant="body2" color="text.secondary">
            未作成
          </Typography>
        ),
    },
  ];

  return (
    <Show
      resource="tests-review"
      goBack={<BackButton />}
      breadcrumb={
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          aria-label="パンくずリスト"
          sx={{
            "& .MuiBreadcrumbs-ol": {
              alignItems: "center",
            },
            "& a": {
              display: "flex",
              alignItems: "center",
              color: "var(--color-green)",
              textDecoration: "none",
              "&:hover": {
                textDecoration: "underline",
              },
            },
          }}
        >
          <Link
            color="inherit"
            href="/tests-review"
            onClick={(e) => {
              e.preventDefault();
              router.push("/tests-review");
            }}
          >
            テスト振り返り
          </Link>
          <Typography
            color="text.primary"
            sx={{ display: "flex", alignItems: "center" }}
          >
            テスト詳細
          </Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          テスト詳細
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      {/* Header section */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
        }}
      >
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="h6"
            sx={{
              display: "flex",
              alignItems: "center",
              color: "var(--color-green)",
            }}
          >
            <DescriptionIcon sx={{ mr: 1 }} />
            個票と答案を表示します。
          </Typography>

          <Typography variant="h5" fontWeight="bold" sx={{ mt: 2 }}>
            {testData.year}年度 {testData.grade} {testData.term}{" "}
            {testData.subject}
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Filters */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="grade-select-label">学年</InputLabel>
              <Select
                labelId="grade-select-label"
                id="grade-select"
                value={selectedGrade}
                label="学年"
                onChange={(e) => {
                  setSelectedGrade(e.target.value);
                  // Reset class when grade changes to avoid invalid combinations
                  setSelectedClass(
                    studentData
                      .filter((s) => s.grade === e.target.value)
                      .map((s) => s.classRoom)[0] || "1"
                  );
                }}
              >
                {grades.map((grade) => (
                  <MenuItem key={grade} value={grade}>
                    {grade}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="class-select-label">クラス</InputLabel>
              <Select
                labelId="class-select-label"
                id="class-select"
                value={selectedClass}
                label="クラス"
                onChange={(e) => setSelectedClass(e.target.value)}
              >
                {classes.map((classRoom) => (
                  <MenuItem key={classRoom} value={classRoom}>
                    {classRoom}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>

          {/* Download buttons */}
          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<FileDownloadIcon />}
              onClick={handleBulkAnswerSheetDownload}
              sx={{
                color: "var(--color-blue)",
                borderColor: "var(--color-blue)",
                "&:hover": { borderColor: "var(--color-blue)", opacity: 0.9 },
              }}
            >
              答案一括DL
            </Button>

            <Button
              variant="outlined"
              startIcon={<FileDownloadIcon />}
              onClick={handleBulkIndividualSheetDownload}
              sx={{
                color: "var(--color-green)",
                borderColor: "var(--color-green)",
                "&:hover": { borderColor: "var(--color-green)", opacity: 0.9 },
              }}
            >
              個票一括DL
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Student table section */}
      <Paper
        elevation={2}
        sx={{
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
          overflow: "hidden",
        }}
      >
        <Box sx={{ maxHeight: 600, overflow: "auto" }}>
          <SharedTable
            columns={columns}
            dataSource={filteredStudents}
            themeColor="var(--color-green)"
          />
        </Box>
      </Paper>
    </Show>
  );
};

export default TestReviewDetailPage;
