import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Divider,
  Stack,
  Tooltip,
  Typography,
  Modal,
  Paper,
  FormControl,
  FormControlLabel,
  Checkbox,
  TextField,
  MenuItem,
  Select,
  InputLabel,
  FormGroup,
  FormLabel,
  IconButton,
  InputAdornment,
} from "@mui/material";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import PersonIcon from "@mui/icons-material/Person";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import SettingsIcon from "@mui/icons-material/Settings";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import LockIcon from "@mui/icons-material/Lock";
import PeopleIcon from "@mui/icons-material/People";
import CloseIcon from "@mui/icons-material/Close";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { ja } from "date-fns/locale/ja";

// Define the test item type
export interface TestItem {
  id: string;
  name: string;
  subject: string;
  testDate: string;
  registrationDate: string;
  propertiesUpdateDate: string;
  feedbackDueDate: string;
  type: string;
  collectionRate?: string; // optional as not all items have this
  individualSheetReturnDate?: string; // optional
  reviewDeadline?: string; // optional
}

// Define the analysis tool type
export interface AnalyzeTool {
  id: string;
  name: string;
  icon: React.ReactNode;
}

interface CardTestReviewProps {
  test: TestItem;
  analyzeTools: AnalyzeTool[];
}

export default function CardTestReview({
  test,
  analyzeTools,
}: CardTestReviewProps) {
  const router = useRouter();

  // State for managing the settings modal
  const [openSettings, setOpenSettings] = useState(false);
  const [selectedAnalysisType, setSelectedAnalysisType] = useState("");
  const [maxReviewQuestions, setMaxReviewQuestions] = useState("5");
  const [returnDate, setReturnDate] = useState<Date | null>(null);
  const [checkedItems, setCheckedItems] = useState({
    item1: true,
    item2: true,
    item3: true,
    item4: true,
    item5: false,
  });

  // Handle checkbox changes
  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCheckedItems({
      ...checkedItems,
      [event.target.name]: event.target.checked,
    });
  };

  // Modal open/close handlers
  const handleOpenSettings = () => setOpenSettings(true);
  const handleCloseSettings = () => setOpenSettings(false);

  return (
    <Card
      key={test.id}
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        borderRadius: "8px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      }}
    >
      <CardContent>
        <Box
          sx={{
            mb: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <Box>
            <Typography
              variant="h6"
              sx={{ color: "var(--color-green)", fontWeight: "bold" }}
            >
              {test.name}
            </Typography>
            <Box
              sx={{
                display: "flex",
                flexWrap: "wrap",
                gap: 1,
                mt: 0.5,
              }}
            >
              <Chip
                size="small"
                label={test.subject}
                sx={{
                  bgcolor: "var(--color-yellow)",
                  color: "white",
                  fontWeight: "bold",
                }}
              />
              <Chip
                size="small"
                label={test.type}
                sx={{
                  bgcolor: "var(--color-blue)",
                  color: "white",
                }}
              />
              {test.collectionRate && (
                <Chip
                  size="small"
                  label={`回収率: ${test.collectionRate}`}
                  sx={{
                    bgcolor: "var(--color-green)",
                    color: "white",
                  }}
                />
              )}
            </Box>
          </Box>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Tooltip title="確認">
              <Button
                size="small"
                variant="outlined"
                startIcon={<CheckCircleIcon />}
                onClick={() => router.push(`/tests-review/${test.id}`)}
                sx={{
                  minWidth: "auto",
                  color: "var(--color-green)",
                  borderColor: "var(--color-green)",
                }}
              >
                確認
              </Button>
            </Tooltip>
            <Tooltip title="公開停止">
              <Button
                size="small"
                variant="outlined"
                startIcon={<LockIcon />}
                sx={{
                  minWidth: "auto",
                  color: "var(--color-red)",
                  borderColor: "var(--color-red)",
                }}
              >
                公開停止
              </Button>
            </Tooltip>
            <Tooltip title="設定">
              <Button
                size="small"
                variant="outlined"
                startIcon={<SettingsIcon />}
                onClick={handleOpenSettings}
                sx={{
                  minWidth: "auto",
                  color: "var(--color-blue)",
                  borderColor: "var(--color-blue)",
                }}
              >
                設定
              </Button>
            </Tooltip>
          </Box>
        </Box>

        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={3}
          divider={<Divider orientation="vertical" flexItem />}
          sx={{ mb: 2 }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <CalendarTodayIcon
              sx={{ mr: 1, color: "var(--color-green)", fontSize: 18 }}
            />
            <Typography variant="body2">
              <strong>実施日:</strong> {test.testDate}
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <EventAvailableIcon
              sx={{ mr: 1, color: "var(--color-green)", fontSize: 18 }}
            />
            <Typography variant="body2">
              <strong>登録完了:</strong> {test.registrationDate}
            </Typography>
          </Box>
        </Stack>

        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={3}
          divider={<Divider orientation="vertical" flexItem />}
          sx={{ mb: 2 }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <PictureAsPdfIcon
              sx={{ mr: 1, color: "var(--color-green)", fontSize: 18 }}
            />
            <Typography variant="body2">
              <strong>問題属性:</strong> {test.propertiesUpdateDate}更新
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <PersonIcon
              sx={{ mr: 1, color: "var(--color-green)", fontSize: 18 }}
            />
            <Typography variant="body2">
              <strong>フィードバック提出期限:</strong> {test.feedbackDueDate}
              まで
            </Typography>
          </Box>
        </Stack>

        {/* Additional information about individual sheet return and review deadline */}
        {(test.individualSheetReturnDate || test.reviewDeadline) && (
          <Box sx={{ bgcolor: "#f6f9ff", p: 1.5, borderRadius: 1, mt: 2 }}>
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={3}
              divider={<Divider orientation="vertical" flexItem />}
            >
              {test.individualSheetReturnDate && (
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <PeopleIcon
                    sx={{ mr: 1, color: "var(--color-blue)", fontSize: 18 }}
                  />
                  <Typography variant="body2">
                    <strong>個票:</strong> {test.individualSheetReturnDate}返却
                  </Typography>
                </Box>
              )}
              {test.reviewDeadline && (
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <EventAvailableIcon
                    sx={{ mr: 1, color: "var(--color-blue)", fontSize: 18 }}
                  />
                  <Typography variant="body2">
                    <strong>振り返り:</strong> {test.reviewDeadline}期限
                  </Typography>
                </Box>
              )}
            </Stack>
          </Box>
        )}
      </CardContent>

      <Divider />
      <CardActions
        sx={{
          p: 2,
          bgcolor: "#f9f9f9",
          mt: "auto",
          flexWrap: "wrap",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            width: "100%",
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
          }}
        >
          <Box sx={{ display: "flex", mb: { xs: 2, md: 0 } }}>
            <Typography
              variant="subtitle2"
              sx={{ mr: 2, color: "#666", whiteSpace: "nowrap" }}
            >
              分析ツール:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {analyzeTools.map((tool) => (
                <Tooltip key={tool.id} title={tool.name} arrow>
                  <Button
                    startIcon={tool.icon}
                    size="small"
                    onClick={() => {
                      if (tool.id === 'lrt') {
                        router.push(`/tests-review/lrt/${test.id}`);
                      } else {
                        // Handle other tool clicks
                        console.log(`Clicked on ${tool.name}`);
                      }
                    }}
                    sx={{
                      borderRadius: "16px",
                      whiteSpace: "nowrap",
                      color: "var(--color-green)",
                      border: "1px solid var(--color-green)",
                      "&:hover": {
                        bgcolor: "rgba(23, 160, 152, 0.1)",
                      },
                    }}
                  >
                    {tool.name}
                  </Button>
                </Tooltip>
              ))}
            </Box>
          </Box>
        </Box>
      </CardActions>

      {/* Settings Modal */}
      <Modal
        open={openSettings}
        onClose={handleCloseSettings}
        aria-labelledby="settings-modal-title"
      >
        <Paper
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "80%",
            maxHeight: "90vh",
            overflow: "auto",
            p: 4,
            borderRadius: 2,
          }}
        >
          {/* Modal Header */}
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
            <Typography
              id="settings-modal-title"
              variant="h6"
              fontWeight="bold"
            >
              個票設定
            </Typography>
            <IconButton onClick={handleCloseSettings} size="small">
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Modal Content */}
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              {test.name} - 個票の設定を行います
            </Typography>

            {/* Analysis Type Selection */}
            <FormControl fullWidth margin="normal">
              <InputLabel id="analysis-type-select-label">
                分析タイプ
              </InputLabel>
              <Select
                labelId="analysis-type-select-label"
                id="analysis-type-select"
                value={selectedAnalysisType}
                label="分析タイプ"
                onChange={(e) => setSelectedAnalysisType(e.target.value)}
              >
                <MenuItem value="type1">項目別分析</MenuItem>
                <MenuItem value="type2">能力別分析</MenuItem>
                <MenuItem value="type3">得点分布分析</MenuItem>
              </Select>
            </FormControl>

            {/* Items to Include Group */}
            <Box sx={{ mt: 3, mb: 3 }}>
              <FormLabel component="legend" sx={{ fontWeight: "bold", mb: 1 }}>
                個票に含める項目
              </FormLabel>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                個票に表示する項目を選択してください。これらの項目は学生に表示されます。
              </Typography>

              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkedItems.item1}
                      onChange={handleCheckboxChange}
                      name="item1"
                    />
                  }
                  label={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Typography variant="body2">成績表 (全体概要)</Typography>
                    </Box>
                  }
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkedItems.item2}
                      onChange={handleCheckboxChange}
                      name="item2"
                    />
                  }
                  label={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Typography variant="body2">項目別診断</Typography>
                      <Tooltip title="各テスト項目ごとの成績を表示します">
                        <HelpOutlineIcon
                          fontSize="small"
                          sx={{ ml: 1, color: "text.secondary" }}
                        />
                      </Tooltip>
                    </Box>
                  }
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkedItems.item3}
                      onChange={handleCheckboxChange}
                      name="item3"
                    />
                  }
                  label={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Typography variant="body2">能力別診断</Typography>
                    </Box>
                  }
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkedItems.item4}
                      onChange={handleCheckboxChange}
                      name="item4"
                    />
                  }
                  label={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Typography variant="body2">平均点比較 ※1</Typography>
                      <Tooltip title="クラス内および学校全体の平均点と比較します">
                        <HelpOutlineIcon
                          fontSize="small"
                          sx={{ ml: 1, color: "text.secondary" }}
                        />
                      </Tooltip>
                    </Box>
                  }
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkedItems.item5}
                      onChange={handleCheckboxChange}
                      name="item5"
                    />
                  }
                  label={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Typography variant="body2">総合分析 ※2</Typography>
                      <Tooltip title="過去のテストデータと比較した総合的な分析を表示します">
                        <HelpOutlineIcon
                          fontSize="small"
                          sx={{ ml: 1, color: "text.secondary" }}
                        />
                      </Tooltip>
                    </Box>
                  }
                />
              </FormGroup>
            </Box>

            {/* Max Review Questions */}
            <FormControl
              fullWidth
              variant="outlined"
              margin="normal"
              sx={{ mb: 3 }}
            >
              <InputLabel htmlFor="max-review-questions">
                復習問題の最大数
              </InputLabel>
              <TextField
                id="max-review-questions"
                label="復習問題の最大数"
                type="number"
                value={maxReviewQuestions}
                onChange={(e) => setMaxReviewQuestions(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">問</InputAdornment>
                  ),
                }}
              />
            </FormControl>

            {/* Return Date Picker */}
            <FormControl fullWidth margin="normal" sx={{ mb: 3 }}>
              <LocalizationProvider
                dateAdapter={AdapterDateFns}
                adapterLocale={ja}
              >
                <DatePicker
                  label="個票返却日"
                  value={returnDate}
                  onChange={(newValue) => {
                    setReturnDate(newValue);
                  }}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: "outlined",
                      helperText: "学生に個票が公開される日付を設定します",
                    },
                  }}
                />
              </LocalizationProvider>
            </FormControl>

            {/* Action Buttons */}
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}
            >
              <Button
                onClick={handleCloseSettings}
                variant="outlined"
                color="inherit"
              >
                キャンセル
              </Button>
              <Box sx={{ display: "flex", gap: 2 }}>
                <Button
                  startIcon={<VisibilityIcon />}
                  variant="outlined"
                  color="primary"
                >
                  プレビュー
                </Button>
                <Button
                  variant="contained"
                  sx={{
                    bgcolor: "var(--color-green)",
                    "&:hover": { bgcolor: "var(--color-dark-green)" },
                  }}
                >
                  保存
                </Button>
              </Box>
            </Box>
          </Box>
        </Paper>
      </Modal>
    </Card>
  );
}
