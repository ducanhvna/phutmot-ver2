"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Typography,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  Select,
  MenuItem,
  Button,
  Chip,
  FormControl,
  InputLabel,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  Checkbox,
  Divider,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import SharedTable, { SharedTableColumn } from "@/components/shared-table";
import { Show } from "@refinedev/mui";

// Types
interface FormData {
  name: string;
  subject: string;
  year: string;
  grade: string;
  class: string;
  status: "実施中" | "終了"; // Active or Complete
  dateRange: string;
  creator: string;
  responses: string;
  id?: string; // Add ID for unique identification
}

interface StudentData {
  id: string;
  grade: string;
  class: string;
  number: number;
  name: string;
  status: string;
  reminderDate: string;
  selected: boolean;
}

// Mock data
const mockData: FormData[] = [
  {
    id: "form1",
    name: "第2回授業理解度",
    subject: "数学A",
    year: "2025",
    grade: "1年",
    class: "1-4",
    status: "実施中",
    dateRange: "2025/06/03-2025/06/20",
    creator: "山田太郎",
    responses: "76|8",
  },
  {
    id: "form2",
    name: "第2回授業理解度",
    subject: "理科基礎",
    year: "2025",
    grade: "1年",
    class: "1-4",
    status: "実施中",
    dateRange: "2025/06/03-2025/06/20",
    creator: "佐々木花",
    responses: "68|14",
  },
  {
    id: "form3",
    name: "第1回授業理解度",
    subject: "数学A",
    year: "2025",
    grade: "2年",
    class: "1-4",
    status: "終了",
    dateRange: "2025/04/21-2025/04/29",
    creator: "山田太郎",
    responses: "70|10",
  },
  {
    id: "form4",
    name: "課題提出",
    subject: "社会/日本史",
    year: "2025",
    grade: "1年",
    class: "1-4",
    status: "終了",
    dateRange: "2025/04/01-2025/04/07",
    creator: "佐藤陽介",
    responses: "46|26",
  },
];

// Mock data for non-responding students
const mockNonRespondingStudents: StudentData[] = [
  {
    id: "s1",
    grade: "1年",
    class: "2組",
    number: 5,
    name: "佐藤 太郎",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s2",
    grade: "1年",
    class: "2組",
    number: 8,
    name: "鈴木 花子",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s3",
    grade: "1年",
    class: "2組",
    number: 12,
    name: "高橋 誠",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s4",
    grade: "1年",
    class: "3組",
    number: 3,
    name: "渡辺 結衣",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s5",
    grade: "1年",
    class: "3組",
    number: 15,
    name: "伊藤 健太",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s6",
    grade: "1年",
    class: "4組",
    number: 1,
    name: "山本 和也",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s7",
    grade: "1年",
    class: "4組",
    number: 11,
    name: "田中 美香",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
  {
    id: "s8",
    grade: "1年",
    class: "4組",
    number: 23,
    name: "小林 大輔",
    status: "未回答",
    reminderDate: "2025/04/28",
    selected: false,
  },
];

export default function DailyProgressTeacherPage() {
  const router = useRouter();

  // State for filters
  const [creatorFilter, setCreatorFilter] = useState<string>("自分");
  const [yearFilter, setYearFilter] = useState<string>("2025");
  const [gradeFilter, setGradeFilter] = useState<string>("1年");
  const [subjectFilter, setSubjectFilter] = useState<string>("数学");
  // State for filtered data
  const [filteredData, setFilteredData] = useState<FormData[]>(mockData);

  // State for popup dialog
  const [dialogOpen, setDialogOpen] = useState<boolean>(false);
  const [currentForm, setCurrentForm] = useState<FormData | null>(null);
  const [nonRespondingStudents, setNonRespondingStudents] = useState<
    StudentData[]
  >(mockNonRespondingStudents);

  // Apply filters
  useEffect(() => {
    const filtered = mockData.filter((item) => {
      // Apply filters based on selected values
      if (gradeFilter && item.grade !== gradeFilter) return false;
      if (subjectFilter && !item.subject.includes(subjectFilter)) return false;
      if (yearFilter && item.year !== yearFilter) return false;
      if (creatorFilter === "自分" && item.creator !== "山田太郎") return false;

      return true;
    });

    setFilteredData(filtered);
  }, [creatorFilter, yearFilter, gradeFilter, subjectFilter]);

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setCurrentForm(null);
  };

  // Handle student selection
  const handleToggleStudent = (id: string) => {
    setNonRespondingStudents((prevStudents) =>
      prevStudents.map((student) =>
        student.id === id
          ? { ...student, selected: !student.selected }
          : student
      )
    );
  };
  // Select/deselect all students
  const handleSelectAllStudents = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isChecked = event.target.checked;
    setNonRespondingStudents((prevStudents) =>
      prevStudents.map((student) => ({ ...student, selected: isChecked }))
    );
  };

  // Send reminders to selected students
  const handleSendReminders = () => {
    const selectedStudents = nonRespondingStudents.filter(
      (student) => student.selected
    );

    // In a real application, you would send the reminders here
    console.log("Sending reminders to:", selectedStudents);

    // Update reminder date for selected students
    const today = new Date().toISOString().split("T")[0].replace(/-/g, "/");

    setNonRespondingStudents((prevStudents) =>
      prevStudents.map((student) =>
        student.selected
          ? { ...student, reminderDate: today, selected: false }
          : student
      )
    );

    // Show success message (in a real app)
    alert(`${selectedStudents.length}人の学生に回答催促を送信しました。`);
  };

  // Column definitions for non-responding students table
  const studentColumns: SharedTableColumn[] = [
    {
      title: "",
      key: "checkbox",
      width: 60,
      render: (_, student) => (
        <Checkbox
          checked={(student as StudentData).selected}
          onChange={() => handleToggleStudent((student as StudentData).id)}
        />
      ),
    },
    {
      title: "学年",
      dataIndex: "grade",
      key: "grade",
      width: 80,
    },
    {
      title: "組",
      dataIndex: "class",
      key: "class",
      width: 80,
    },
    {
      title: "番号",
      dataIndex: "number",
      key: "number",
      width: 60,
    },
    {
      title: "氏名",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "回答状況",
      key: "status",
      render: (_, student) => (
        <Chip
          label={(student as StudentData).status}
          size="small"
          sx={{
            bgcolor: "var(--color-yellow)",
            color: "white",
            fontWeight: "medium",
            borderRadius: "16px",
          }}
        />
      ),
    },
    {
      title: "回答催促日",
      dataIndex: "reminderDate",
      key: "reminderDate",
    },
  ];

  // Column definitions for the table
  const columns: SharedTableColumn[] = [
    {
      title: "名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "教科・科目",
      dataIndex: "subject",
      key: "subject",
    },
    {
      title: "年度",
      dataIndex: "year",
      key: "year",
      width: 80,
    },
    {
      title: "学年",
      dataIndex: "grade",
      key: "grade",
      width: 80,
    },
    {
      title: "クラス・グループ",
      dataIndex: "class",
      key: "class",
      width: 150,
    },
    {
      title: "ステータス",
      key: "status",
      width: 120,
      render: (text, record) => (
        <Chip
          label={record.status}
          color={record.status === "実施中" ? "success" : "default"}
          sx={{
            borderRadius: "16px",
            backgroundColor:
              record.status === "実施中"
                ? "var(--color-green)"
                : "var(--color-disabled)",
            color: "white",
            fontWeight: "medium",
          }}
        />
      ),
    },
    {
      title: "開始日 終了日",
      dataIndex: "dateRange",
      key: "dateRange",
      width: 180,
    },
    {
      title: "作成者",
      key: "creator",
      render: (text, record) => <Typography>{record.creator}</Typography>,
    },
    {
      title: "回答状況",
      key: "responses",
      render: (text, record) => {
        const [completed, pending] = record.responses.split("|").map(Number);
        const total = completed + pending;
        const completedPercentage = Math.round((completed / total) * 100);

        return (
          <Box
            sx={{ width: "100%", my: 1, cursor: "pointer" }}
            onClick={() => {
              setCurrentForm(record);
              setDialogOpen(true);
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                mb: 0.5,
              }}
            >
              <Typography variant="body2">{`${completed}/${total}`}</Typography>
              <Typography variant="body2">{`${completedPercentage}%`}</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={completedPercentage}
              sx={{
                height: 8,
                borderRadius: 5,
                backgroundColor: "var(--color-yellow)",
                "& .MuiLinearProgress-bar": {
                  backgroundColor:
                    completedPercentage > 80
                      ? "var(--color-green)"
                      : completedPercentage > 50
                      ? "var(--color-blue)"
                      : "var(--color-yellow)",
                },
              }}
            />
          </Box>
        );
      },
    },
    {
      title: "回答内容",
      key: "actions",
      width: 100,
      render: (text, record) => (
        <Tooltip title="詳細を表示">
          <IconButton
            size="small"
            sx={{
              color: "var(--color-blue)",
              "&:hover": {
                backgroundColor: "rgba(30, 160, 215, 0.1)",
              },
            }}
          >
            <VisibilityIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          日々の学習記録
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: 4,
        },
      }}
    >
      {/* Filters */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              sm: "1fr 1fr",
              md: "1fr 1fr 1fr",
            },
            gap: 3,
          }}
        >
          {/* Creator Filter */}
          <Box>
            <Typography
              variant="subtitle1"
              sx={{ mb: 1, fontWeight: "medium" }}
            >
              作成者:
            </Typography>
            <ToggleButtonGroup
              value={creatorFilter}
              exclusive
              onChange={(_, value) => value && setCreatorFilter(value)}
              fullWidth
              size="small"
              sx={{
                border: "1px solid rgba(0, 0, 0, 0.12)",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <ToggleButton
                value="自分"
                sx={{
                  bgcolor:
                    creatorFilter === "自分"
                      ? "var(--color-green)"
                      : "var(--color-main-secondary)",
                  color: creatorFilter === "自分" ? "white" : "black",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                  },
                  "&:hover": {
                    bgcolor:
                      creatorFilter === "自分"
                        ? "var(--color-green)"
                        : "#e0e0e0",
                    opacity: 0.9,
                  },
                  transition: "all 0.2s ease",
                }}
              >
                自分
              </ToggleButton>
              <ToggleButton
                value="全体"
                sx={{
                  bgcolor:
                    creatorFilter === "全体"
                      ? "var(--color-green)"
                      : "var(--color-main-secondary)",
                  color: creatorFilter === "全体" ? "white" : "black",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                  },
                  "&:hover": {
                    bgcolor:
                      creatorFilter === "全体"
                        ? "var(--color-green)"
                        : "#e0e0e0",
                    opacity: 0.9,
                  },
                  transition: "all 0.2s ease",
                }}
              >
                全体
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Year Filter */}
          <Box>
            <Typography
              variant="subtitle1"
              sx={{ mb: 1, fontWeight: "medium" }}
            >
              年度：
            </Typography>
            <FormControl fullWidth>
              <InputLabel id="year-select-label">年度</InputLabel>
              <Select
                labelId="year-select-label"
                value={yearFilter}
                label="年度"
                onChange={(e) => setYearFilter(e.target.value as string)}
                size="small"
              >
                <MenuItem value="2025">2025</MenuItem>
                <MenuItem value="2024">2024</MenuItem>
                <MenuItem value="2023">2023</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Grade Filter */}
          <Box>
            <Typography
              variant="subtitle1"
              sx={{ mb: 1, fontWeight: "medium" }}
            >
              学年:
            </Typography>
            <ToggleButtonGroup
              value={gradeFilter}
              exclusive
              onChange={(_, value) => value && setGradeFilter(value)}
              fullWidth
              size="small"
              sx={{
                border: "1px solid rgba(0, 0, 0, 0.12)",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <ToggleButton
                value="1年"
                sx={{
                  bgcolor:
                    gradeFilter === "1年"
                      ? "var(--color-green)"
                      : "var(--color-main-secondary)",
                  color: gradeFilter === "1年" ? "white" : "black",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                  },
                  "&:hover": {
                    bgcolor:
                      gradeFilter === "1年" ? "var(--color-green)" : "#e0e0e0",
                    opacity: 0.9,
                  },
                  transition: "all 0.2s ease",
                }}
              >
                1年
              </ToggleButton>
              <ToggleButton
                value="2年"
                sx={{
                  bgcolor:
                    gradeFilter === "2年"
                      ? "var(--color-green)"
                      : "var(--color-main-secondary)",
                  color: gradeFilter === "2年" ? "white" : "black",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                  },
                  "&:hover": {
                    bgcolor:
                      gradeFilter === "2年" ? "var(--color-green)" : "#e0e0e0",
                    opacity: 0.9,
                  },
                  transition: "all 0.2s ease",
                }}
              >
                2年
              </ToggleButton>
              <ToggleButton
                value="3年"
                sx={{
                  bgcolor:
                    gradeFilter === "3年"
                      ? "var(--color-green)"
                      : "var(--color-main-secondary)",
                  color: gradeFilter === "3年" ? "white" : "black",
                  "&.Mui-selected": {
                    bgcolor: "var(--color-green)",
                    color: "white",
                  },
                  "&:hover": {
                    bgcolor:
                      gradeFilter === "3年" ? "var(--color-green)" : "#e0e0e0",
                    opacity: 0.9,
                  },
                  transition: "all 0.2s ease",
                }}
              >
                3年
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Subject Filter - Full width across all columns */}
          <Box
            sx={{ gridColumn: { xs: "1", sm: "1 / span 2", md: "1 / span 3" } }}
          >
            <Typography
              variant="subtitle1"
              sx={{ mb: 1, fontWeight: "medium" }}
            >
              教科・科目:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {[
                "数学",
                "理科",
                "英語",
                "音楽",
                "保健体育",
                "技術家庭",
                "道徳",
                "特活",
                "総合",
              ].map((subject) => (
                <ToggleButton
                  key={subject}
                  value={subject}
                  selected={subjectFilter === subject}
                  onChange={() => setSubjectFilter(subject)}
                  size="small"
                  sx={{
                    bgcolor:
                      subjectFilter === subject
                        ? "var(--color-yellow)"
                        : "var(--color-main-secondary)",
                    color: subjectFilter === subject ? "white" : "black",
                    "&.Mui-selected": {
                      bgcolor: "var(--color-yellow)",
                      color: "white",
                    },
                    "&:hover": {
                      bgcolor:
                        subjectFilter === subject
                          ? "var(--color-yellow)"
                          : "#e0e0e0",
                      opacity: 0.9,
                    },
                    mb: 1,
                    borderRadius: "16px",
                    transition: "all 0.2s ease",
                  }}
                >
                  {subject}
                </ToggleButton>
              ))}
            </Box>
          </Box>
        </Box>
      </Paper>
      {/* Create New Form Button */}
      <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => router.push("/daily-progress-teacher/create")}
          sx={{
            bgcolor: "var(--color-green)",
            color: "white",
            fontWeight: "medium",
            px: 3,
            borderRadius: 2,
            boxShadow: 2,
            "&:hover": {
              bgcolor: "var(--color-green)",
              opacity: 0.9,
              boxShadow: 3,
            },
            transition: "all 0.3s ease",
          }}
          size="medium"
        >
          新規フォーム作成
        </Button>
      </Box>
      {/* Main Data Table */}
      <Box
        sx={{
          boxShadow: 2,
          borderRadius: 2,
          overflow: "hidden",
          backgroundColor: "#ffffff",
          "& .MuiTableCell-root": {
            py: 2,
            px: 3,
          },
          "& .MuiTableRow-root:hover": {
            backgroundColor: "rgba(23, 160, 152, 0.04)",
          },
        }}
      >
        <SharedTable
          dataSource={filteredData}
          columns={columns}
          themeColor="var(--color-green)"
        />
      </Box>
      {/* Non-responding Students Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxHeight: "90vh",
          },
        }}
      >
        <DialogTitle
          sx={{
            bgcolor: "var(--color-green)",
            color: "white",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            px: 3,
            py: 2,
          }}
        >
          <Typography variant="h6" component="div" sx={{ fontWeight: "bold" }}>
            {currentForm?.name}：{currentForm?.subject}　未回答者一覧
          </Typography>
          <IconButton
            edge="end"
            color="inherit"
            onClick={handleCloseDialog}
            aria-label="close"
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ px: 3, py: 2 }}>
          <Box sx={{ mb: 2 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: "bold" }}>
                未回答の生徒一覧
              </Typography>
              <Box>
                <Checkbox
                  indeterminate={
                    nonRespondingStudents.some((s) => s.selected) &&
                    !nonRespondingStudents.every((s) => s.selected)
                  }
                  checked={nonRespondingStudents.every((s) => s.selected)}
                  onChange={handleSelectAllStudents}
                  sx={{ mr: 1 }}
                />
                <Typography variant="body2" component="span">
                  全選択
                </Typography>
              </Box>
            </Box>
            <Box sx={{ maxHeight: "400px", overflow: "auto" }}>
              <SharedTable
                dataSource={nonRespondingStudents}
                columns={studentColumns}
                themeColor="var(--color-green)"
              />
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: "flex", justifyContent: "center" }}>
            <Button
              variant="contained"
              onClick={handleSendReminders}
              disabled={!nonRespondingStudents.some((s) => s.selected)}
              sx={{
                bgcolor: "var(--color-blue)",
                color: "white",
                fontWeight: "medium",
                px: 4,
                py: 1,
                borderRadius: 2,
                "&:hover": {
                  bgcolor: "var(--color-blue)",
                  opacity: 0.9,
                },
                "&.Mui-disabled": {
                  bgcolor: "var(--color-disabled)",
                  color: "white",
                },
                transition: "all 0.3s ease",
              }}
            >
              回答催促ボタン
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Show>
  );
}
