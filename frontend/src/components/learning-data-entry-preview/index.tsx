"use client";

import {
  Typography,
  Paper,
  Box,
  Button,
  Stack,
  Alert,
  Breadcrumbs,
} from "@mui/material";
import Link from "next/link";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import ErrorIcon from "@mui/icons-material/Error";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CancelIcon from "@mui/icons-material/Cancel";
import SharedTable from "@/components/shared-table";
import { Create } from "@refinedev/mui";
import { useRouter } from "next/navigation";

interface LearningDataEntryPreviewProps {
  previewData: any[];
  tableColumns: any[];
  filterData: {
    educationalSystem: string;
    year: string;
    subject: string;
    subSubject: string;
  };
  hasError: boolean;
  uploadError: string | null;
  onCancel: () => void;
  onSubmit: () => void;
  formLoading: boolean;
  saveButtonProps: any;
}

export default function LearningDataEntryPreview({
  previewData,
  tableColumns,
  filterData,
  hasError,
  uploadError,
  onCancel,
  onSubmit,
  formLoading,
  saveButtonProps,
}: LearningDataEntryPreviewProps) {
  const router = useRouter();

  return (
    <Create
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
      title={
        <Typography variant="h5" fontWeight="700">
          学習データ登録プレビュー
        </Typography>
      }
      saveButtonProps={{
        ...saveButtonProps,
        sx: { display: "none" }, // Hide the default save button
      }}
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
            href="/learning-data-entry"
            onClick={(e) => {
              e.preventDefault();
              router.push("/learning-data-entry");
            }}
          >
            学習データ登録履歴
          </Link>
          <Link
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onCancel();
            }}
          >
            学習データ登録
          </Link>
          <Typography
            color="text.primary"
            sx={{ display: "flex", alignItems: "center" }}
          >
            学習データ登録プレビュー
          </Typography>
        </Breadcrumbs>
      }
    >
      {/* Error message if CSV has errors */}
      {uploadError && (
        <Alert
          severity="error"
          icon={<ErrorIcon />}
          sx={{
            mb: 3,
            borderRadius: "10px",
            "& .MuiAlert-message": {
              fontWeight: "medium",
            },
          }}
        >
          {uploadError}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 3, borderRadius: "10px", mb: 4 }}>
        <Typography
          variant="h6"
          sx={{
            mb: 3,
            borderBottom: "2px solid var(--color-green)",
            pb: 1,
            fontWeight: "bold",
          }}
        >
          フィルター情報
        </Typography>

        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, mb: 1 }}>
          <Box
            sx={{ minWidth: { xs: "100%", sm: "30%", md: "23%" }, flexGrow: 1 }}
          >
            <Typography variant="body2" color="text.secondary">
              教材システム
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {filterData.educationalSystem}
            </Typography>
          </Box>

          <Box
            sx={{ minWidth: { xs: "100%", sm: "30%", md: "23%" }, flexGrow: 1 }}
          >
            <Typography variant="body2" color="text.secondary">
              年度
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {filterData.year}
            </Typography>
          </Box>

          <Box
            sx={{ minWidth: { xs: "100%", sm: "30%", md: "23%" }, flexGrow: 1 }}
          >
            <Typography variant="body2" color="text.secondary">
              教科
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {filterData.subject}
            </Typography>
          </Box>

          <Box
            sx={{ minWidth: { xs: "100%", sm: "30%", md: "23%" }, flexGrow: 1 }}
          >
            <Typography variant="body2" color="text.secondary">
              科目
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {filterData.subSubject}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {hasError && (
        <Alert
          severity="error"
          icon={<ErrorIcon />}
          sx={{
            mb: 3,
            borderRadius: "10px",
            "& .MuiAlert-message": {
              fontWeight: "medium",
            },
          }}
        >
          CSVデータの読み込みに問題がありました。
          <br />
          再度、ファイルを選択してください。
        </Alert>
      )}

      {!hasError && previewData.length === 0 && (
        <Alert
          severity="info"
          sx={{
            mb: 3,
            borderRadius: "10px",
            "& .MuiAlert-message": {
              fontWeight: "medium",
            },
          }}
        >
          CSVデータが見つかりませんでした。アップロードページに戻って再度お試しください。
        </Alert>
      )}

      {/* Data preview table */}
      <Paper
        elevation={3}
        sx={{ borderRadius: "10px", mb: 4, overflow: "hidden", p: 3 }}
      >
        <Box sx={{ pb: 2 }}>
          <Typography
            variant="h6"
            sx={{
              mb: 3,
              borderBottom: "2px solid var(--color-green)",
              pb: 1,
              fontWeight: "bold",
            }}
          >
            データプレビュー
          </Typography>
        </Box>

        <Box sx={{ maxHeight: "400px", overflow: "auto" }}>
          {previewData.length > 0 ? (
            <SharedTable
              dataSource={previewData}
              columns={
                tableColumns.length > 0
                  ? tableColumns
                  : [
                      {
                        key: "id",
                        title: "基盤学習者ID",
                        dataIndex: "id",
                      },
                      {
                        key: "fullName",
                        title: "基盤学習者姓名",
                        dataIndex: "fullName",
                      },
                      {
                        key: "year",
                        title: "年度",
                        dataIndex: "year",
                      },
                      {
                        key: "grade",
                        title: "学年",
                        dataIndex: "grade",
                      },
                      {
                        key: "group",
                        title: "組",
                        dataIndex: "group",
                      },
                      {
                        key: "name",
                        title: "氏名",
                        dataIndex: "name",
                      },
                      {
                        key: "unitName",
                        title: "単元名称",
                        dataIndex: "unitName",
                      },
                      {
                        key: "studyHours",
                        title: "学習時間",
                        dataIndex: "studyHours",
                      },
                    ]
              }
              themeColor="var(--color-green)"
            />
          ) : (
            <Typography variant="body1" sx={{ textAlign: "center", p: 4 }}>
              データが見つかりませんでした。CSVファイルをアップロードしてください。
            </Typography>
          )}
        </Box>
      </Paper>

      {/* Action buttons */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        justifyContent="center"
        alignItems="center"
      >
        <Button
          variant="outlined"
          startIcon={<CancelIcon />}
          onClick={onCancel}
          sx={{
            minWidth: { xs: "100%", sm: "200px" },
            color: "var(--color-gray)",
            borderColor: "var(--color-gray)",
            "&:hover": {
              borderColor: "var(--color-green)",
              color: "var(--color-green)",
            },
          }}
        >
          キャンセル
        </Button>

        <Button
          variant="contained"
          startIcon={<CheckCircleOutlineIcon />}
          onClick={onSubmit}
          sx={{
            minWidth: { xs: "100%", sm: "200px" },
            backgroundColor: "var(--color-green)",
            "&:hover": {
              backgroundColor: "var(--color-green)",
              opacity: 0.9,
            },
          }}
        >
          こちらの内容で登録します
        </Button>
      </Stack>
    </Create>
  );
}
