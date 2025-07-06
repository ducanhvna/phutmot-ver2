"use client";

import { useState } from "react";
import {
  Typography,
  Box,
  Paper,
  Stack,
  ToggleButtonGroup,
  ToggleButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
} from "@mui/material";
import CardTestReview from "@components/card-test-review";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { ja } from "date-fns/locale";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import SchoolIcon from "@mui/icons-material/School";
import DescriptionIcon from "@mui/icons-material/Description";
import TimelineIcon from "@mui/icons-material/Timeline";
import AssessmentIcon from "@mui/icons-material/Assessment";
import VisibilityIcon from "@mui/icons-material/Visibility";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import { Show } from "@refinedev/mui";
import EmailIcon from "@mui/icons-material/Email";

const TestReviewPage: React.FC = () => {
  // State for filters
  const [year, setYear] = useState<string>("2025");
  const [grade, setGrade] = useState<string>("2年");
  const [classRoom, setClassRoom] = useState<string>("1組");
  const [group, setGroup] = useState<string>("");
  const [startDate, setStartDate] = useState<Date | null>(
    new Date("2025-06-21")
  );
  const [endDate, setEndDate] = useState<Date | null>(new Date("2025-07-20"));
  const [testType, setTestType] = useState<string>("定期テスト");
  const [schoolType, setSchoolType] = useState<string>("中学校");
  const [subject, setSubject] = useState<string>("数学");
  // Mock test data
  const testItems = [
    {
      id: "1",
      name: "1学期末考査 数学",
      subject: "数学",
      testDate: "2025/7/19",
      registrationDate: "2025/7/18 9:33",
      propertiesUpdateDate: "2025/7/19 9:30",
      feedbackDueDate: "2025/7/25",
      type: "定期テスト",
      collectionRate: "200/200",
      individualSheetReturnDate: "2025/7/25",
      reviewDeadline: "2025/8/3",
    },
    {
      id: "2",
      name: "1学期末考査 英語",
      subject: "英語",
      testDate: "2025/7/19",
      registrationDate: "2025/7/18 9:38",
      propertiesUpdateDate: "2025/7/19 9:35",
      feedbackDueDate: "2025/8/3",
      type: "定期テスト",
      collectionRate: "198/200",
      individualSheetReturnDate: "2025/7/25",
      reviewDeadline: "2025/8/3",
    },
    {
      id: "3",
      name: "1学期末考査 国語",
      subject: "国語",
      testDate: "2025/7/20",
      registrationDate: "2025/7/18 10:15",
      propertiesUpdateDate: "2025/7/19 11:30",
      feedbackDueDate: "2025/7/27",
      type: "定期テスト",
    },
    {
      id: "4",
      name: "理科実験テスト",
      subject: "理科",
      testDate: "2025/7/21",
      registrationDate: "2025/7/19 14:22",
      propertiesUpdateDate: "2025/7/20 8:45",
      feedbackDueDate: "2025/7/28",
      type: "実力テスト",
    },
    {
      id: "5",
      name: "歴史小テスト",
      subject: "社会",
      testDate: "2025/7/15",
      registrationDate: "2025/7/14 16:05",
      propertiesUpdateDate: "2025/7/14 17:20",
      feedbackDueDate: "2025/7/22",
      type: "小テスト",
    },
    {
      id: "6",
      name: "技術実習評価",
      subject: "技術",
      testDate: "2025/7/12",
      registrationDate: "2025/7/11 11:33",
      propertiesUpdateDate: "2025/7/11 15:00",
      feedbackDueDate: "2025/7/19",
      type: "その他テスト",
    },
    {
      id: "7",
      name: "音楽実技テスト",
      subject: "音楽",
      testDate: "2025/7/10",
      registrationDate: "2025/7/09 10:45",
      propertiesUpdateDate: "2025/7/09 14:30",
      feedbackDueDate: "2025/7/17",
      type: "実力テスト",
    },
    {
      id: "8",
      name: "美術作品評価",
      subject: "美術",
      testDate: "2025/7/05",
      registrationDate: "2025/7/04 13:20",
      propertiesUpdateDate: "2025/7/04 16:40",
      feedbackDueDate: "2025/7/15",
      type: "その他テスト",
    },
    {
      id: "9",
      name: "高校入試模擬試験",
      subject: "英語",
      testDate: "2025/7/01",
      registrationDate: "2025/6/30 09:15",
      propertiesUpdateDate: "2025/6/30 17:00",
      feedbackDueDate: "2025/7/10",
      type: "模擬試験",
    },
    {
      id: "10",
      name: "家庭科実習評価",
      subject: "家庭科",
      testDate: "2025/6/28",
      registrationDate: "2025/6/27 14:30",
      propertiesUpdateDate: "2025/6/27 17:15",
      feedbackDueDate: "2025/7/05",
      type: "その他テスト",
    },
    {
      id: "11",
      name: "体力測定テスト",
      subject: "体育",
      testDate: "2025/6/25",
      registrationDate: "2025/6/24 10:00",
      propertiesUpdateDate: "2025/6/24 15:40",
      feedbackDueDate: "2025/7/02",
      type: "実力テスト",
    },
    {
      id: "12",
      name: "総合学力テスト",
      subject: "数学",
      testDate: "2025/6/22",
      registrationDate: "2025/6/21 09:20",
      propertiesUpdateDate: "2025/6/21 14:10",
      feedbackDueDate: "2025/6/29",
      type: "定期テスト",
    },
  ];

  // Lists for filters
  const years = ["2025", "2026", "2027"];
  const grades = ["1年", "2年", "3年"];
  const classes = ["1組", "2組", "3組", "4組", "5組"];
  const testTypes = [
    "定期テスト",
    "実力テスト",
    "模擬試験",
    "小テスト",
    "その他テスト",
  ];
  const schoolTypes = ["中学校", "高等学校", "小学校", "幼稚園"];
  const subjects = [
    "数学",
    "国語",
    "理科",
    "社会",
    "技術",
    "家庭科",
    "音楽",
    "美術",
    "体育",
    "英語",
  ];

  // Analysis tools
  const analyzeTools = [
    { id: "lrt", name: "設問分析", icon: <TimelineIcon /> },
    {
      id: "realtrendant",
      name: "RealtenDantツール",
      icon: <AssessmentIcon />,
    },
    { id: "aggregate", name: "集計分析", icon: <AnalyticsIcon /> },
    { id: "teachers-eye", name: "Teacher's Eye", icon: <VisibilityIcon /> },
    { id: "ai-tool", name: "AIツール", icon: <PictureAsPdfIcon /> },
    { id: "mail", name: "一括回答依頼", icon: <EmailIcon /> },
  ];

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          テスト振り返り
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      {/* Filter section */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <FilterAltIcon sx={{ color: "var(--color-green)", mr: 1 }} />
          <Typography variant="h6" fontWeight="bold" color="var(--color-green)">
            フィルター
          </Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          {/* First row of filters */}
          <Stack
            direction={{ xs: "column", md: "row" }}
            spacing={2}
            sx={{ mb: 3 }}
          >
            {/* Year filter */}
            <FormControl size="small" sx={{ minWidth: 120, flexGrow: 1 }}>
              <InputLabel>年度</InputLabel>
              <Select
                value={year}
                label="年度"
                onChange={(e) => setYear(e.target.value)}
              >
                {years.map((y) => (
                  <MenuItem key={y} value={y}>
                    {y}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Grade filter */}
            <FormControl size="small" sx={{ minWidth: 120, flexGrow: 1 }}>
              <InputLabel>学年</InputLabel>
              <Select
                value={grade}
                label="学年"
                onChange={(e) => setGrade(e.target.value)}
              >
                {grades.map((g) => (
                  <MenuItem key={g} value={g}>
                    {g}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Class filter */}
            <FormControl size="small" sx={{ minWidth: 120, flexGrow: 1 }}>
              <InputLabel>クラス</InputLabel>
              <Select
                value={classRoom}
                label="クラス"
                onChange={(e) => setClassRoom(e.target.value)}
              >
                {classes.map((c) => (
                  <MenuItem key={c} value={c}>
                    {c}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Group filter */}
            <TextField
              label="グループ"
              size="small"
              value={group}
              onChange={(e) => setGroup(e.target.value)}
              sx={{ minWidth: 120, flexGrow: 1 }}
            />
          </Stack>

          {/* Second row of filters */}
          <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
            {/* Test period filter */}
            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                gap: 1,
                flexGrow: 1,
              }}
            >
              <Typography
                sx={{ alignSelf: "center", whiteSpace: "nowrap", mr: 1 }}
              >
                テスト実施期間:
              </Typography>
              <LocalizationProvider
                dateAdapter={AdapterDateFns}
                adapterLocale={ja}
              >
                <DatePicker
                  label="開始日"
                  value={startDate}
                  onChange={setStartDate}
                  slotProps={{ textField: { size: "small" } }}
                  sx={{ flexGrow: 1 }}
                />
                <Typography sx={{ alignSelf: "center", mx: 1 }}>～</Typography>
                <DatePicker
                  label="終了日"
                  value={endDate}
                  onChange={setEndDate}
                  slotProps={{ textField: { size: "small" } }}
                  sx={{ flexGrow: 1 }}
                />
              </LocalizationProvider>
            </Box>

            {/* Test type filter */}
            <FormControl size="small" sx={{ minWidth: 200, flexGrow: 1 }}>
              <InputLabel>テスト分類</InputLabel>
              <Select
                value={testType}
                label="テスト分類"
                onChange={(e) => setTestType(e.target.value)}
              >
                {testTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </Box>

        {/* School type section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 1 }}>
            <SchoolIcon
              sx={{ fontSize: 20, verticalAlign: "text-bottom", mr: 1 }}
            />
            学校タイプ
          </Typography>
          <ToggleButtonGroup
            value={schoolType}
            exclusive
            onChange={(_, value) => value && setSchoolType(value)}
            aria-label="school type"
            size="small"
            sx={{ flexWrap: "wrap" }}
          >
            {schoolTypes.map((type) => (
              <ToggleButton
                key={type}
                value={type}
                sx={{
                  px: 3,
                  bgcolor:
                    schoolType === type ? "var(--color-green)" : "transparent",
                  color: schoolType === type ? "white" : "inherit",
                  border: "1px solid var(--color-green)",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                    "&:hover": {
                      bgcolor: "var(--color-green)",
                      opacity: 0.9,
                    },
                  },
                  "&:hover": {
                    bgcolor:
                      schoolType === type
                        ? "var(--color-green)"
                        : "rgba(23, 160, 152, 0.1)",
                  },
                }}
              >
                {type}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>

        {/* Subject section */}
        <Box>
          <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 1 }}>
            <DescriptionIcon
              sx={{ fontSize: 20, verticalAlign: "text-bottom", mr: 1 }}
            />
            科目
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {subjects.map((sub) => (
              <Chip
                key={sub}
                label={sub}
                onClick={() => setSubject(sub)}
                sx={{
                  bgcolor:
                    subject === sub ? "var(--color-yellow)" : "transparent",
                  color: subject === sub ? "white" : "inherit",
                  border: "1px solid var(--color-yellow)",
                  "&:hover": {
                    bgcolor:
                      subject === sub
                        ? "var(--color-yellow)"
                        : "rgba(242, 152, 0, 0.1)",
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      </Paper>
      {/* Test results section */}
      <Typography
        variant="h6"
        fontWeight="bold"
        sx={{
          mb: 2,
          display: "flex",
          alignItems: "center",
          color: "var(--color-green)",
        }}
      >
        <AnalyticsIcon sx={{ mr: 1 }} />
        テスト結果 ({testItems.length}件)
      </Typography>

      <Box sx={{ mb: 4 }}>
        {/* Use flexbox to create a layout with 2 items per row */}
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          {testItems.map((test) => (
            <CardTestReview
              key={test.id}
              test={test}
              analyzeTools={analyzeTools}
            />
          ))}
        </Box>
      </Box>
    </Show>
  );
};

export default TestReviewPage;
