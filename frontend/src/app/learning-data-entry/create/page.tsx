"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Create } from "@refinedev/mui";
import { useForm } from "@refinedev/react-hook-form";
import Link from "next/link";
import {
  Typography,
  Box,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  TextField,
  Breadcrumbs,
  Stack,
  styled,
} from "@mui/material";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import DownloadIcon from "@mui/icons-material/Download";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import ErrorIcon from "@mui/icons-material/Error";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CancelIcon from "@mui/icons-material/Cancel";
import SharedTable from "@/components/shared-table";
import LearningDataEntryPreview from "@/components/learning-data-entry-preview";

// Styled component for the file drop zone
const DropZone = styled(Box)(({ theme }) => ({
  border: "2px dashed var(--color-gray)",
  borderRadius: "10px",
  padding: "40px 20px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
  backgroundColor: "#fafafa",
  transition: "border .3s, background-color .3s",
  "&:hover": {
    borderColor: "var(--color-green)",
    backgroundColor: "#f0f9f9",
  },
}));

export default function LearningDataEntryCreate() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Preview related states
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [tableColumns, setTableColumns] = useState<any[]>([]);
  const [filterData, setFilterData] = useState({
    educationalSystem: "",
    year: "",
    subject: "",
    subSubject: "",
  });
  const [hasError, setHasError] = useState(false);

  // Using Refine's form hook
  const {
    saveButtonProps,
    refineCore: { formLoading },
    control,
    formState: { errors },
    setValue,
    watch,
  } = useForm({
    refineCoreProps: {
      resource: "learning-data-entry",
      redirect: "list",
    },
  });

  // Options for dropdowns
  const educationalSystems = ["ドリルパーク", "スタディサプリⅠ型", "その他"];
  const years = ["2025", "2026", "2027"];
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
  const subSubjects = {
    math: ["数A", "数B", "数Ⅰ", "数Ⅱ", "数Ⅲ"],
    japanese: ["現代文", "古文", "漢文"],
    english: ["英語表現", "コミュニケーション英語", "リーディング"],
    science: ["物理", "化学", "生物", "地学"],
    social: ["日本史", "世界史", "地理", "公民"],
    tech: ["情報処理", "工業"],
    home: ["調理", "被服"],
    music: ["声楽", "器楽"],
    art: ["絵画", "彫刻", "デザイン"],
    pe: ["球技", "陸上", "水泳"],
  };

  // Watch for subject changes to update sub-subjects
  const selectedSubject = watch("subject");
  const availableSubSubjects = selectedSubject
    ? subSubjects[selectedSubject as keyof typeof subSubjects] || []
    : [];

  // Handle file drop and selection
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      const droppedFile = droppedFiles[0];
      if (droppedFile.name.endsWith(".csv")) {
        setFile(droppedFile);
        setUploadError(null);
      } else {
        setUploadError("CSVファイルのみアップロード可能です");
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith(".csv")) {
        setFile(selectedFile);
        setUploadError(null);
      } else {
        setUploadError("CSVファイルのみアップロード可能です");
      }
    }
  };

  const handleTemplateDownload = () => {
    console.log("Downloading template...");
    // Implement download functionality
  };

  // Parse CSV function
  const parseCSV = (csvContent: string) => {
    try {
      // Split content into rows, handling both \r\n and \n line endings
      const rows = csvContent.split(/\r?\n/);

      // Get headers from the first row
      const headers = rows[0].split(",").map((header) => header.trim());
      console.log("CSV Headers:", headers);

      const data = [];

      // Process each data row
      for (let i = 1; i < rows.length; i++) {
        // Skip empty rows
        if (!rows[i] || rows[i].trim() === "") continue;

        // Split the row into values
        const values = rows[i].split(",").map((value) => value.trim());

        // Create an object with header keys and row values
        const rowData: Record<string, string> = {};

        headers.forEach((header, index) => {
          // Ensure we have a valid header and assign the value or empty string
          if (header) {
            rowData[header] = values[index] || "";
          }
        });

        data.push(rowData);
      }

      console.log("Parsed CSV data:", data);
      return { headers, data };
    } catch (error) {
      console.error("Error parsing CSV:", error);
      throw new Error("CSV解析中にエラーが発生しました");
    }
  };

  const handleUpload = () => {
    if (!file) {
      setUploadError("ファイルが選択されていません");
      return;
    }

    // Get selected values from the form
    const educationalSystem = watch("educationalSystem");
    const year = watch("year");
    const subject = watch("subject");
    const subSubject = watch("subSubject");

    // Check if required filters are selected
    if (!educationalSystem || !year || !subject || !subSubject) {
      setUploadError("すべてのフィルターを選択してください");
      return;
    }

    // Read and parse the CSV file
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const { headers, data } = parseCSV(content);

        // Get subject name instead of ID
        const selectedSubject = subjects.find((s) => s.id === subject)?.name || "";

        // Create filter data object
        const updatedFilterData = {
          educationalSystem,
          year,
          subject: selectedSubject,
          subSubject,
        };

        // Set the data for preview
        setFilterData(updatedFilterData);
        setPreviewData(data);

        // Create columns for the table based on CSV headers
        const columns = headers.map((header: string) => {
          // Map common Japanese headers to more readable titles
          const titleMap: { [key: string]: string } = {
            id: "基盤学習者ID",
            fullName: "基盤学習者姓名",
            year: "年度",
            grade: "学年",
            group: "組",
            name: "氏名",
            unitName: "単元名称",
            studyHours: "学習時間",
            // Add more mappings as needed
          };

          return {
            key: header,
            title: titleMap[header] || header, // Use mapping if available, otherwise use the header as is
            dataIndex: header,
          };
        });

        setTableColumns(columns);
        setHasError(false);

        // Show the preview section
        setShowPreview(true);
      } catch (error) {
        console.error("Error parsing CSV:", error);
        setUploadError("CSVファイルの解析中にエラーが発生しました");
        setHasError(true);
      }
    };

    reader.onerror = () => {
      setUploadError("ファイルの読み込み中にエラーが発生しました");
      setHasError(true);
    };

    reader.readAsText(file);
  };

  // Handle cancel (return to upload view)
  const handleCancel = () => {
    console.log("Cancelling data submission");
    setShowPreview(false);
    setPreviewData([]);
    setTableColumns([]);
  };

  // Handle submit (register data)
  const handleRegisterData = async () => {
    try {
      console.log("Registering data:", { filterData, previewData });

      // In a real implementation, you would send the data to the server
      // For example:
      /*
      const response = await fetch('/api/learning-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filterData,
          data: previewData
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to register data');
      }
      
      const result = await response.json();
      console.log("API response:", result);
      */

      // Simulate successful API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Reset the form
      setShowPreview(false);
      setPreviewData([]);
      setTableColumns([]);
      setFile(null);
      setValue("educationalSystem", "");
      setValue("year", "");
      setValue("subject", "");
      setValue("subSubject", "");

      // If successful, redirect to list page
      router.push("/learning-data-entry");
    } catch (error) {
      console.error("Error registering data:", error);
      setHasError(true);
      // Show error message in real application
      setUploadError("データ登録中にエラーが発生しました");
    }
  };

  return showPreview ? (
    <LearningDataEntryPreview 
      previewData={previewData}
      tableColumns={tableColumns}
      filterData={filterData}
      hasError={hasError}
      uploadError={uploadError}
      onCancel={handleCancel}
      onSubmit={handleRegisterData}
      formLoading={formLoading}
      saveButtonProps={saveButtonProps}
    />
  ) : (
    <Create
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
      title={
        <Typography variant="h5" fontWeight="700">
          学習データ登録
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
            color="inherit"
            href="/learning-data-entry"
            onClick={(e) => {
              e.preventDefault();
              router.push("/learning-data-entry");
            }}
          >
            学習データ登録履歴
          </Link>
          <Typography
            color="text.primary"
            sx={{ display: "flex", alignItems: "center" }}
          >
            学習データ登録
          </Typography>
        </Breadcrumbs>
      }
    >
      {/* Error message */}
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

      <Box component="form">
        <Box sx={{ mb: 4 }}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: "10px" }}>
            <Typography
              variant="h6"
              sx={{
                mb: 3,
                borderBottom: "2px solid var(--color-green)",
                pb: 1,
                fontWeight: "bold",
              }}
            >
              データフィルター
            </Typography>

            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, mb: 3 }}>
              {/* Educational System */}
              <FormControl
                sx={{
                  minWidth: { xs: "100%", sm: "30%", md: "23%" },
                  flexGrow: 1,
                }}
              >
                <InputLabel>教材システム</InputLabel>
                <Select
                  label="教材システム"
                  defaultValue=""
                  onChange={(e) =>
                    setValue("educationalSystem", e.target.value)
                  }
                  sx={{
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "var(--color-green)",
                    },
                  }}
                >
                  {educationalSystems.map((system) => (
                    <MenuItem key={system} value={system}>
                      {system}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Year */}
              <FormControl
                sx={{
                  minWidth: { xs: "100%", sm: "30%", md: "23%" },
                  flexGrow: 1,
                }}
              >
                <InputLabel>年度</InputLabel>
                <Select
                  label="年度"
                  defaultValue=""
                  onChange={(e) => setValue("year", e.target.value)}
                  sx={{
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "var(--color-green)",
                    },
                  }}
                >
                  {years.map((year) => (
                    <MenuItem key={year} value={year}>
                      {year}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Subject */}
              <FormControl
                sx={{
                  minWidth: { xs: "100%", sm: "30%", md: "23%" },
                  flexGrow: 1,
                }}
              >
                <InputLabel>教科</InputLabel>
                <Select
                  label="教科"
                  defaultValue=""
                  onChange={(e) => setValue("subject", e.target.value)}
                  sx={{
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "var(--color-green)",
                    },
                  }}
                >
                  {subjects.map((subject) => (
                    <MenuItem key={subject.id} value={subject.id}>
                      {subject.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Sub-Subject */}
              <FormControl
                sx={{
                  minWidth: { xs: "100%", sm: "30%", md: "23%" },
                  flexGrow: 1,
                }}
                disabled={!selectedSubject || availableSubSubjects.length === 0}
              >
                <InputLabel>科目</InputLabel>
                <Select
                  label="科目"
                  defaultValue=""
                  onChange={(e) => setValue("subSubject", e.target.value)}
                  sx={{
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: "var(--color-green)",
                    },
                  }}
                >
                  {availableSubSubjects.map((subSubject) => (
                    <MenuItem key={subSubject} value={subSubject}>
                      {subSubject}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </Paper>
        </Box>

        {/* CSV Upload Section */}
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
            新規学習データ登録
          </Typography>

          <input
            type="file"
            accept=".csv"
            id="csv-upload"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />

          <label htmlFor="csv-upload">
            <DropZone
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              sx={{
                borderColor: isDragging
                  ? "var(--color-green)"
                  : "var(--color-gray)",
                backgroundColor: isDragging ? "#f0f9f9" : "#fafafa",
                mb: 3,
              }}
            >
              <UploadFileIcon
                sx={{ fontSize: 48, color: "var(--color-green)", mb: 2 }}
              />
              <Typography variant="h6" gutterBottom align="center">
                CSVデータをドラッグアンドドロップ
              </Typography>
              <Typography variant="body2" color="textSecondary" align="center">
                または、クリックしてファイルを選択
              </Typography>
              {file && (
                <Typography sx={{ mt: 2, color: "var(--color-green)" }}>
                  選択済み: {file.name}
                </Typography>
              )}
            </DropZone>
          </label>
        </Paper>

        {/* Action buttons */}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          justifyContent="flex-end"
          alignItems="center"
        >
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleTemplateDownload}
            sx={{
              color: "var(--color-gray)",
              borderColor: "var(--color-gray)",
              "&:hover": {
                borderColor: "var(--color-green)",
                color: "var(--color-green)",
              },
            }}
          >
            テンプレートDL
          </Button>

          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              onClick={handleUpload}
              disabled={!file}
              sx={{
                backgroundColor: "var(--color-green)",
                "&:hover": {
                  backgroundColor: "var(--color-green)",
                  opacity: 0.9,
                },
                "&.Mui-disabled": {
                  backgroundColor: "var(--color-gray)",
                },
              }}
            >
              アップロード
            </Button>
          </Box>
        </Stack>
      </Box>
    </Create>
  );
}
