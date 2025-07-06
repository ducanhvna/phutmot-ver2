"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Stack,
  Breadcrumbs,
  Link,
  Tabs,
  Tab,
} from "@mui/material";
import { Show } from "@refinedev/mui";
import { useRouter, useParams } from "next/navigation";
import { useBack } from "@refinedev/core";
import dynamic from "next/dynamic";

// Icons
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import TimelineIcon from "@mui/icons-material/Timeline";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningIcon from "@mui/icons-material/Warning";
import InsightsIcon from "@mui/icons-material/Insights";

// Components
import SharedTable, { SharedTableColumn } from "@/components/shared-table";

// Import Plotly dynamically to avoid SSR issues
const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <div>Loading chart...</div>,
}) as any;

// Mock test data
const testData = {
  id: "1",
  name: "1学期末考査 数学",
  year: "2025",
  grade: "2年",
  term: "1学期期末テスト",
  subject: "数学",
  testDate: "2025/7/19",
  totalQuestions: 30,
  totalStudents: 120,
};

// Mock question group data
const questionGroups = [
  {
    id: "1",
    title: "グループ 1 (問題 1-5)",
    questions: [1, 2, 3, 4, 5],
    correctRate: 78,
    trend: [65, 70, 78, 76, 78],
  },
  {
    id: "2",
    title: "グループ 2 (問題 6-10)",
    questions: [6, 7, 8, 9, 10],
    correctRate: 62,
    trend: [60, 58, 59, 65, 62],
  },
  {
    id: "3",
    title: "グループ 3 (問題 11-15)",
    questions: [11, 12, 13, 14, 15],
    correctRate: 45,
    trend: [38, 42, 40, 44, 45],
  },
  {
    id: "4",
    title: "グループ 4 (問題 16-20)",
    questions: [16, 17, 18, 19, 20],
    correctRate: 68,
    trend: [58, 62, 65, 67, 68],
  },
  {
    id: "5",
    title: "グループ 5 (問題 21-25)",
    questions: [21, 22, 23, 24, 25],
    correctRate: 85,
    trend: [75, 78, 82, 84, 85],
  },
  {
    id: "6",
    title: "グループ 6 (問題 26-30)",
    questions: [26, 27, 28, 29, 30],
    correctRate: 52,
    trend: [42, 45, 48, 50, 52],
  },
];

// Mock question analysis data
const questionAnalysisData = [
  {
    id: "1",
    question: "問1",
    correctRate: 88,
    difficulty: "易しい",
    discriminationIndex: 0.75,
    status: "good",
    type: "選択肢",
  },
  {
    id: "2",
    question: "問2",
    correctRate: 85,
    difficulty: "易しい",
    discriminationIndex: 0.72,
    status: "good",
    type: "選択肢",
  },
  {
    id: "3",
    question: "問3",
    correctRate: 72,
    difficulty: "普通",
    discriminationIndex: 0.68,
    status: "good",
    type: "選択肢",
  },
  {
    id: "4",
    question: "問4",
    correctRate: 68,
    difficulty: "普通",
    discriminationIndex: 0.35,
    status: "warning",
    type: "選択肢",
  },
  {
    id: "5",
    question: "問5",
    correctRate: 43,
    difficulty: "難しい",
    discriminationIndex: 0.28,
    status: "error",
    type: "選択肢",
  },
];

// Summary data for footer
const questionTypeSummary = [
  { type: "選択肢", count: 20 },
  { type: "記述", count: 8 },
  { type: "穴埋め", count: 2 },
];

export default function ViewDetailLRTPage() {
  const router = useRouter();
  const params = useParams();
  const goBack = useBack();
  const testId = params.id as string;

  // State for selected tab and selected question group
  const [tabValue, setTabValue] = useState(0);
  const [selectedGroup, setSelectedGroup] = useState(questionGroups[0]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleGroupSelect = (group: any) => {
    setSelectedGroup(group);
  };

  // Status renderer for table
  const renderStatus = (status: string) => {
    switch (status) {
      case "good":
        return (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-green)",
            }}
          >
            <CheckCircleIcon fontSize="small" sx={{ marginRight: 0.5 }} />
            <Typography variant="body2">良い</Typography>
          </Box>
        );
      case "warning":
        return (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-yellow)",
            }}
          >
            <WarningIcon fontSize="small" sx={{ marginRight: 0.5 }} />
            <Typography variant="body2">要注意</Typography>
          </Box>
        );
      case "error":
        return (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-red)",
            }}
          >
            <ErrorIcon fontSize="small" sx={{ marginRight: 0.5 }} />
            <Typography variant="body2">問題あり</Typography>
          </Box>
        );
      default:
        return null;
    }
  };

  // Define column for analysis table
  const columns: SharedTableColumn[] = [
    {
      title: "問題番号",
      dataIndex: "question",
      key: "question",
      width: 100,
    },
    {
      title: "正答率",
      dataIndex: "correctRate",
      key: "correctRate",
      width: 100,
      render: (text) => `${text}%`,
    },
    {
      title: "難易度",
      dataIndex: "difficulty",
      key: "difficulty",
      width: 100,
    },
    {
      title: "識別指数",
      dataIndex: "discriminationIndex",
      key: "discriminationIndex",
      width: 100,
    },
    {
      title: "状態",
      dataIndex: "status",
      key: "status",
      width: 120,
      render: (_, record) => renderStatus(record.status),
    },
    {
      title: "問題タイプ",
      dataIndex: "type",
      key: "type",
      width: 100,
    },
  ];

  // Function to get color based on correct rate
  const getColorByRate = (rate: number) => {
    if (rate >= 75) return "var(--color-green)";
    if (rate >= 50) return "var(--color-yellow)";
    return "var(--color-red)";
  };

  const BackButton = () => {
    return (
      <IconButton onClick={goBack}>
        <ArrowBackIcon />
      </IconButton>
    );
  };

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
          <Typography color="text.primary">設問分析 (LRT)</Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          設問分析 (LRT)
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      <Box sx={{ width: "100%" }}>
        {/* Header Section */}
        <Box sx={{ mb: 3 }}>
          <Paper sx={{ p: 2, backgroundColor: "var(--color-main)" }}>
            <Stack
              direction={{ xs: "column", md: "row" }}
              spacing={3}
              justifyContent="space-between"
            >
              <Box>
                <Typography variant="h6">{testData.name}</Typography>
                <Typography variant="body2">
                  {testData.grade} | {testData.term} | {testData.subject} |
                  実施日: {testData.testDate}
                </Typography>
              </Box>
              <Stack direction="row" spacing={2}>
                <Box sx={{ textAlign: "center" }}>
                  <Typography variant="body2" color="text.secondary">
                    問題数
                  </Typography>
                  <Typography variant="h6">
                    {testData.totalQuestions}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: "center" }}>
                  <Typography variant="body2" color="text.secondary">
                    受験者数
                  </Typography>
                  <Typography variant="h6">{testData.totalStudents}</Typography>
                </Box>
              </Stack>
            </Stack>
          </Paper>
        </Box>

        {/* Analysis Type Tabs */}
        <Box sx={{ width: "100%", mb: 3 }}>
          <Paper sx={{ borderRadius: 1 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant="fullWidth"
              textColor="primary"
              indicatorColor="primary"
              sx={{
                "& .MuiTab-root": {
                  minHeight: "64px",
                  fontWeight: "bold",
                },
              }}
            >
              <Tab
                icon={<AnalyticsIcon />}
                label="項目分析"
                iconPosition="start"
                sx={{
                  color: tabValue === 0 ? "var(--color-green)" : "inherit",
                }}
              />
              <Tab
                icon={<AssessmentIcon />}
                label="識別力分析"
                iconPosition="start"
                sx={{
                  color: tabValue === 1 ? "var(--color-blue)" : "inherit",
                }}
              />
              <Tab
                icon={<TimelineIcon />}
                label="難易度分析"
                iconPosition="start"
                sx={{
                  color: tabValue === 2 ? "var(--color-yellow)" : "inherit",
                }}
              />
              <Tab
                icon={<InsightsIcon />}
                label="総合分析"
                iconPosition="start"
                sx={{
                  color: tabValue === 3 ? "var(--color-red)" : "inherit",
                }}
              />
            </Tabs>
          </Paper>
        </Box>

        {/* Question Groups Horizontal Scroll */}
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
          問題グループ
        </Typography>
        <Box
          sx={{
            display: "flex",
            overflowX: "auto",
            gap: 2,
            pb: 1,
            mb: 3,
            "&::-webkit-scrollbar": {
              height: "8px",
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: "rgba(0, 0, 0, 0.2)",
              borderRadius: "4px",
            },
          }}
        >
          {questionGroups.map((group) => (
            <Paper
              key={group.id}
              sx={{
                p: 1.5,
                width: "220px",
                flexShrink: 0,
                cursor: "pointer",
                border:
                  selectedGroup.id === group.id
                    ? `2px solid var(--color-green)`
                    : "none",
                backgroundColor:
                  selectedGroup.id === group.id
                    ? "var(--color-main)"
                    : "var(--color-white)",
              }}
              onClick={() => handleGroupSelect(group)}
            >
              <Typography variant="body1" fontWeight="bold" sx={{ mb: 1 }}>
                {group.title}
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  正答率
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight="bold"
                  sx={{ color: getColorByRate(group.correctRate) }}
                >
                  {group.correctRate}%
                </Typography>
              </Box>
              <Box sx={{ height: "40px" }}>
                {typeof window !== "undefined" && (
                  <Plot
                    data={[
                      {
                        y: group.trend,
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { color: getColorByRate(group.correctRate) },
                        line: { color: getColorByRate(group.correctRate) },
                      },
                    ]}
                    layout={{
                      margin: { t: 5, r: 5, l: 5, b: 5 },
                      height: 40,
                      width: 190,
                      showlegend: false,
                      xaxis: {
                        showticklabels: false,
                        showgrid: false,
                        zeroline: false,
                      },
                      yaxis: {
                        showticklabels: false,
                        showgrid: false,
                        zeroline: false,
                        range: [0, 100],
                      },
                    }}
                    config={{ displayModeBar: false }}
                  />
                )}
              </Box>
            </Paper>
          ))}
        </Box>

        {/* Main Chart Section */}
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
          {selectedGroup.title} - トレンド分析
        </Typography>
        <Paper sx={{ p: 2, mb: 3, height: "300px" }}>
          {typeof window !== "undefined" && (
            <Plot
              data={[
                {
                  x: selectedGroup.questions,
                  y: selectedGroup.trend,
                  type: "scatter",
                  mode: "lines+markers",
                  marker: {
                    color: getColorByRate(selectedGroup.correctRate),
                    size: 8,
                  },
                  line: {
                    color: getColorByRate(selectedGroup.correctRate),
                    width: 2,
                  },
                  name: "正答率",
                },
              ]}
              layout={{
                autosize: true,
                margin: { t: 10, r: 30, l: 30, b: 30 },
                height: 270,
                showlegend: false,
                xaxis: {
                  title: "問題番号",
                  tickvals: selectedGroup.questions,
                  ticktext: selectedGroup.questions.map((q) => `問${q}`),
                },
                yaxis: {
                  title: "正答率 (%)",
                  range: [0, 100],
                  ticksuffix: "%",
                },
              }}
              config={{
                displayModeBar: false,
                responsive: true,
              }}
              style={{ width: "100%", height: "100%" }}
            />
          )}
        </Paper>

        {/* Results Analysis Table */}
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
          詳細分析
        </Typography>
        <SharedTable
          dataSource={questionAnalysisData}
          columns={columns}
          themeColor="var(--color-green)"
        />

        {/* Footer Summary */}
        <Paper
          sx={{ p: 2, mt: 3, backgroundColor: "var(--color-main-secondary)" }}
        >
          <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
            問題タイプ概要
          </Typography>
          <Stack direction="row" spacing={4}>
            {questionTypeSummary.map((item, index) => (
              <Box key={index}>
                <Typography variant="body2" color="text.secondary">
                  {item.type}
                </Typography>
                <Typography variant="h6">{item.count}問</Typography>
              </Box>
            ))}
            <Box>
              <Typography variant="body2" color="text.secondary">
                合計
              </Typography>
              <Typography variant="h6">
                {questionTypeSummary.reduce((acc, curr) => acc + curr.count, 0)}
                問
              </Typography>
            </Box>
          </Stack>
        </Paper>
      </Box>
    </Show>
  );
}
