"use client";
import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Stack,
  Tooltip,
} from "@mui/material";
import {
  FilterAlt as FilterAltIcon,
  Info as InfoIcon,
  Dashboard as DashboardIcon,
  Description as DescriptionIcon,
  OpenInNew as OpenInNewIcon,
  AssessmentOutlined as AssessmentOutlinedIcon,
} from "@mui/icons-material";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { Show } from "@refinedev/mui";

export default function LearningOverviewPage() {
  // State for filters
  const [year, setYear] = useState<string>("2025");
  const [grade, setGrade] = useState<string>("2");
  const [classRoom, setClassRoom] = useState<string>("1");
  const [studentName, setStudentName] = useState<string>("山田 太郎");
  const [startDate, setStartDate] = useState<Date | null>(
    new Date("2025-04-01")
  );
  const [endDate, setEndDate] = useState<Date | null>(new Date());

  // Lists for filters
  const years = ["2024", "2025", "2026", "2027"];
  const grades = ["1", "2", "3"];
  const classes = ["1", "2", "3", "4", "5"];

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          学習概況
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      {/* Filter section - Report Target Settings */}
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
            レポート対象設定
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
                onChange={(e) => setYear(e.target.value as string)}
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
                onChange={(e) => setGrade(e.target.value as string)}
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
                onChange={(e) => setClassRoom(e.target.value as string)}
              >
                {classes.map((c) => (
                  <MenuItem key={c} value={c}>
                    {c}組
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Student name filter */}
            <TextField
              label="氏名"
              size="small"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              sx={{ minWidth: 120, flexGrow: 1 }}
            />
          </Stack>

          {/* Learning period filter */}
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", sm: "row" },
              gap: 1,
              alignItems: "center",
            }}
          >
            <Typography sx={{ whiteSpace: "nowrap", mr: 1 }}>
              学習期間:
            </Typography>
            <Box sx={{ display: "flex", gap: 1, flexGrow: 1 }}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="開始日"
                  value={startDate}
                  onChange={setStartDate}
                  slotProps={{ textField: { size: "small" } }}
                  sx={{ flexGrow: 1 }}
                />
                <DatePicker
                  label="終了日"
                  value={endDate}
                  onChange={setEndDate}
                  slotProps={{ textField: { size: "small" } }}
                  sx={{ flexGrow: 1 }}
                />
              </LocalizationProvider>
            </Box>
            <Tooltip title="デフォルトで開始日をその年度の4月1日とし、終了日を本日とする">
              <InfoIcon sx={{ color: "var(--color-yellow)", ml: 1 }} />
            </Tooltip>
          </Box>
        </Box>

        {/* Button for viewing cross-subject report */}
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
          }}
        >
          <Button
            variant="contained"
            startIcon={<DescriptionIcon />}
            endIcon={<OpenInNewIcon />}
            sx={{
              bgcolor: "var(--color-green)",
              "&:hover": { bgcolor: "var(--color-green)", opacity: 0.9 },
              mb: 1,
            }}
          >
            教科横断レポート表示
          </Button>
          <Typography variant="caption" sx={{ color: "var(--color-blue)" }}>
            ※レポートは新しいタブで開きます。複数レポートを同時に開くこともできます。
          </Typography>
        </Box>
      </Paper>

      {/* Dashboard section */}
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
          <DashboardIcon sx={{ color: "var(--color-green)", mr: 1 }} />
          <Typography variant="h6" fontWeight="bold" color="var(--color-green)">
            総合分析ダッシュボード
          </Typography>
        </Box>

        <Typography variant="body2" sx={{ mb: 2 }}>
          学年単位・クラス単位でのダッシュボード分析を行いたい場合は、以下のボタンより...
        </Typography>

        <Button
          variant="contained"
          startIcon={<AssessmentOutlinedIcon />}
          endIcon={<OpenInNewIcon />}
          sx={{
            bgcolor: "var(--color-yellow)",
            "&:hover": { bgcolor: "var(--color-yellow)", opacity: 0.9 },
          }}
        >
          総合分析ダッシュボード
        </Button>
      </Paper>
    </Show>
  );
}
