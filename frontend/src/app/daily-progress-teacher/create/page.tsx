"use client";

import { Create } from "@refinedev/mui";
import { useForm } from "@refinedev/react-hook-form";
import React from "react";
import {
  TextField,
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Button,
  Typography,
  Paper,
  FormHelperText,
  Stack,
  Breadcrumbs,
  Link,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { ja } from "date-fns/locale";
import { Controller } from "react-hook-form";
import { useRouter } from "next/navigation";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import TemplateUploadImage from "@components/template-upload-image";
import { TemplateFeedbackPub } from "@components/template-feedback-pub";

export default function DailyProgressTeacherCreate() {
  const router = useRouter();

  // Using Refine's form hook
  const {
    saveButtonProps,
    refineCore: { formLoading },
    register,
    control,
    formState: { errors },
    handleSubmit,
    setValue,
    watch,
  } = useForm({
    refineCoreProps: {
      resource: "daily-progress-teacher",
      redirect: "list",
    },
  });

  // Watch for form type and subject changes
  const selectedFormType = watch("formType") || "授業理解度";
  const selectedSubject = watch("subject");

  // List of years, grades, and classes for dropdowns
  const years = ["2025", "2026", "2027"];
  const grades = ["1年", "2年", "3年"];
  const classes = ["1組", "2組", "3組", "4組", "5組"];
  const groups = ["グループA", "グループB", "グループC", "全員"];

  // List of subjects
  const subjects = [
    { id: "math", name: "数学" },
    { id: "japanese", name: "国語" },
    { id: "english", name: "英語" },
    { id: "science", name: "理科" },
    { id: "social", name: "社会" },
    { id: "tech", name: "技術" },
    { id: "home", name: "家庭科" },
    { id: "music", name: "音楽" },
    { id: "art", name: "美術" },
    { id: "pe", name: "体育" },
  ];

  // Form type options
  const formTypes = [
    { id: "understanding", name: "授業理解度" },
    { id: "image", name: "画像登録" },
  ];
  // Handle subject selection
  const handleSubjectSelect = (subject: string) => {
    setValue("subject", subject);
  };
  // Handle form type selection
  const handleFormTypeSelect = (type: string) => {
    setValue("formType", type);
  };

  // Form submission is handled by Refine through saveButtonProps
  return (
    <div>
      <Create
        wrapperProps={{
          sx: {
            backgroundColor: "var(--color-main)",
            padding: 4,
          },
        }}
        title={
          <Typography variant="h5" fontWeight="700">
            日々の進捗記録フォーム作成
          </Typography>
        }
        saveButtonProps={saveButtonProps}
        isLoading={formLoading}
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
              href="/daily-progress-teacher"
              onClick={(e) => {
                e.preventDefault();
                router.push("/daily-progress-teacher");
              }}
            >
              授業記録フォーム一覧
            </Link>
            <Typography
              color="text.primary"
              sx={{ display: "flex", alignItems: "center" }}
            >
              日々の進捗記録フォーム作成
            </Typography>
          </Breadcrumbs>
        }
      >
        <Box component="form" onSubmit={handleSubmit(() => {})}>
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              gap: 4,
            }}
          >
            {/* Left side - Basic information */}
            <Box
              sx={{
                flex: 1,
                width: { xs: "100%", md: "50%" },
              }}
            >
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  mb: 2,
                  borderRadius: "10px",
                  height: "100%",
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    mb: 3,
                    borderBottom: "2px solid var(--color-green)",
                    pb: 1,

                    fontWeight: "bold",
                  }}
                >
                  基本情報
                </Typography>
                {/* 名称 (Name) */}
                <Box sx={{ mb: 3 }}>
                  <Controller
                    control={control}
                    name="formName"
                    rules={{ required: "名称は必須項目です" }}
                    defaultValue=""
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="名称"
                        placeholder="授業名または内容を入力"
                        required
                        error={!!errors.formName}
                        helperText={errors.formName?.message as string}
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            "&:hover fieldset": {
                              borderColor: "var(--color-green)",
                            },
                            "&.Mui-focused fieldset": {
                              borderColor: "var(--color-green)",
                            },
                          },
                        }}
                      />
                    )}
                  />
                </Box>
                {/* Status and Year */}
                <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
                  <Controller
                    control={control}
                    name="status"
                    defaultValue="実施中"
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.status}>
                        <InputLabel>ステータス</InputLabel>
                        <Select
                          {...field}
                          label="ステータス"
                          sx={{
                            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                              borderColor: "var(--color-green)",
                            },
                          }}
                        >
                          <MenuItem value="実施中">実施中</MenuItem>
                          <MenuItem value="終了">終了</MenuItem>
                        </Select>
                        {errors.status && (
                          <FormHelperText error>
                            {errors.status.message as string}
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />

                  <Controller
                    control={control}
                    name="year"
                    defaultValue="2025"
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.year}>
                        <InputLabel>年度</InputLabel>
                        <Select
                          {...field}
                          label="年度"
                          sx={{
                            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                              borderColor: "var(--color-green)",
                            },
                          }}
                        >
                          {years.map((y) => (
                            <MenuItem key={y} value={y}>
                              {y}年度
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.year && (
                          <FormHelperText error>
                            {errors.year.message as string}
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />
                </Box>
                {/* Grade, Class, Group */}
                <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
                  <Controller
                    control={control}
                    name="grade"
                    defaultValue=""
                    rules={{ required: "学年は必須項目です" }}
                    render={({ field }) => (
                      <FormControl
                        sx={{ minWidth: "30%", flexGrow: 1 }}
                        error={!!errors.grade}
                      >
                        <InputLabel>学年</InputLabel>
                        <Select
                          {...field}
                          label="学年"
                          sx={{
                            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                              borderColor: "var(--color-green)",
                            },
                          }}
                        >
                          {grades.map((g) => (
                            <MenuItem key={g} value={g}>
                              {g}
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.grade && (
                          <FormHelperText error>
                            {errors.grade.message as string}
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />

                  <Controller
                    control={control}
                    name="className"
                    defaultValue=""
                    rules={{ required: "クラスは必須項目です" }}
                    render={({ field }) => (
                      <FormControl
                        sx={{ minWidth: "30%", flexGrow: 1 }}
                        error={!!errors.className}
                      >
                        <InputLabel>クラス</InputLabel>
                        <Select
                          {...field}
                          label="クラス"
                          sx={{
                            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                              borderColor: "var(--color-green)",
                            },
                          }}
                        >
                          {classes.map((c) => (
                            <MenuItem key={c} value={c}>
                              {c}
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.className && (
                          <FormHelperText error>
                            {errors.className.message as string}
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />

                  <Controller
                    control={control}
                    name="group"
                    defaultValue=""
                    render={({ field }) => (
                      <FormControl
                        sx={{ minWidth: "30%", flexGrow: 1 }}
                        error={!!errors.group}
                      >
                        <InputLabel>グループ</InputLabel>
                        <Select
                          {...field}
                          label="グループ"
                          sx={{
                            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                              borderColor: "var(--color-green)",
                            },
                          }}
                        >
                          {groups.map((g) => (
                            <MenuItem key={g} value={g}>
                              {g}
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.group && (
                          <FormHelperText error>
                            {errors.group.message as string}
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />
                </Box>
                {/* Date Range */}
                <Box sx={{ mb: 3 }}>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{
                      fontWeight: "medium",
                    }}
                  >
                    期間
                  </Typography>
                  <Stack direction="row" spacing={2}>
                    <Box sx={{ width: "50%" }}>
                      <Controller
                        control={control}
                        name="startDate"
                        defaultValue={new Date()}
                        render={({ field }) => (
                          <LocalizationProvider
                            dateAdapter={AdapterDateFns}
                            adapterLocale={ja}
                          >
                            <DatePicker
                              {...field}
                              label="開始日"
                              sx={{ width: "100%" }}
                            />
                          </LocalizationProvider>
                        )}
                      />
                    </Box>
                    <Box sx={{ width: "50%" }}>
                      <Controller
                        control={control}
                        name="endDate"
                        defaultValue={new Date()}
                        render={({ field }) => (
                          <LocalizationProvider
                            dateAdapter={AdapterDateFns}
                            adapterLocale={ja}
                          >
                            <DatePicker
                              {...field}
                              label="終了日"
                              sx={{ width: "100%" }}
                            />
                          </LocalizationProvider>
                        )}
                      />
                    </Box>
                  </Stack>
                </Box>
                {/* Subject Selection */}
                <Box sx={{ mb: 3 }}>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{
                      fontWeight: "medium",
                    }}
                  >
                    教科・科目
                  </Typography>
                  <Controller
                    control={control}
                    name="subject"
                    defaultValue=""
                    rules={{ required: "教科・科目は必須項目です" }}
                    render={({ field }) => (
                      <Box>
                        <input type="hidden" {...field} />
                        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                          {subjects.map((subject) => (
                            <Box key={subject.id} sx={{ mb: 1 }}>
                              <Button
                                variant={
                                  selectedSubject === subject.id
                                    ? "contained"
                                    : "outlined"
                                }
                                onClick={() => handleSubjectSelect(subject.id)}
                                sx={{
                                  bgcolor:
                                    selectedSubject === subject.id
                                      ? "var(--color-green)"
                                      : "white",
                                  color:
                                    selectedSubject === subject.id
                                      ? "white"
                                      : "text.primary",
                                  "&:hover": {
                                    bgcolor:
                                      selectedSubject === subject.id
                                        ? "#0E8A82"
                                        : "white",
                                  },
                                  borderRadius: "20px",
                                  transition: "all 0.2s ease",
                                }}
                              >
                                {subject.name}
                              </Button>
                            </Box>
                          ))}
                        </Box>
                        {errors.subject && (
                          <FormHelperText error>
                            {errors.subject.message as string}
                          </FormHelperText>
                        )}
                      </Box>
                    )}
                  />
                </Box>
                {/* Form Type Selection */}
                <Box>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{
                      fontWeight: "medium",
                    }}
                  >
                    記録タイプ
                  </Typography>
                  <Controller
                    control={control}
                    name="formType"
                    defaultValue="授業理解度"
                    render={({ field }) => (
                      <Box>
                        <input type="hidden" {...field} />
                        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                          {formTypes.map((type) => (
                            <Box key={type.id}>
                              <Button
                                variant={
                                  selectedFormType === type.name
                                    ? "contained"
                                    : "outlined"
                                }
                                onClick={() => handleFormTypeSelect(type.name)}
                                sx={{
                                  minWidth: 120,
                                  bgcolor:
                                    selectedFormType === type.name
                                      ? "var(--color-yellow)"
                                      : "transparent",
                                  color:
                                    selectedFormType === type.name
                                      ? "white"
                                      : "var(--color-yellow)",
                                  border:
                                    selectedFormType === type.name
                                      ? "none"
                                      : "1px solid var(--color-yellow)",
                                  "&:hover": {
                                    bgcolor:
                                      selectedFormType === type.name
                                        ? "#D08E1F"
                                        : "rgba(229, 157, 38, 0.1)",
                                  },
                                  borderRadius: "20px",
                                  transition: "all 0.2s ease",
                                }}
                              >
                                {type.name}
                              </Button>
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    )}
                  />
                </Box>
              </Paper>
            </Box>

            {/* Right side - Question Forms */}
            <Box
              sx={{
                flex: 1,
                width: { xs: "100%", md: "50%" },
              }}
            >
              {selectedFormType === "授業理解度" ? (
                <TemplateFeedbackPub control={control} />
              ) : (
                <TemplateUploadImage />
              )}
            </Box>
          </Box>
        </Box>
      </Create>
    </div>
  );
}
