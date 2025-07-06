import { Box, Button, Paper, Typography } from "@mui/material";

export default function TemplateUploadImage() {
  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        borderRadius: "10px",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Typography
        variant="h6"
        sx={{
          mb: 3,
          borderBottom: "2px solid var(--color-yellow)",
          pb: 1,

          fontWeight: "bold",
        }}
      >
        画像登録フォーム
      </Typography>
      {/* Question 1 */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="subtitle1"
          gutterBottom
          sx={{
            fontWeight: "medium",
            backgroundColor: "rgba(229, 157, 38, 0.1)",
            p: 1.5,
            borderRadius: "5px",
            borderLeft: "4px solid var(--color-yellow)",
          }}
        >
          【質問１】授業で指示があった通りに、写真を撮影して送信してください。
        </Typography>
      </Box>
      {/* Image Upload Area */}
      <Box
        sx={{
          width: "100%",
          border: "2px dashed var(--color-green)",
          borderRadius: "8px",
          p: 3,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "rgba(30, 160, 151, 0.05)",
          mb: 3,
          minHeight: "200px",
          transition: "all 0.3s ease",
          "&:hover": {
            backgroundColor: "rgba(30, 160, 151, 0.1)",
            cursor: "pointer",
          },
        }}
      >
        <Typography sx={{ mb: 2 }}>
          ファイルをこのエリアにドラッグ＆ドロップしてください（複数選択可）
        </Typography>
        <Button
          variant="outlined"
          component="label"
          sx={{
            borderColor: "var(--color-green)",
            color: "var(--color-green)",
            "&:hover": {
              borderColor: "var(--color-green)",
              backgroundColor: "rgba(30, 160, 151, 0.1)",
            },
            mb: 2,
          }}
        >
          フォルダに保存した写真を選択する
          <input
            type="file"
            hidden
            multiple
            accept="image/*"
            onChange={(e) => {
              // Handle file selection logic here
              console.log(e.target.files);
            }}
          />
        </Button>
      </Box>
      {/* Submit Button */}
      <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
        <Button
          variant="contained"
          sx={{
            bgcolor: "var(--color-yellow)",
            color: "white",
            px: 4,
            py: 1,
            borderRadius: "20px",
            "&:hover": {
              bgcolor: "#D08E1F",
            },
          }}
        >
          公開
        </Button>
      </Box>
    </Paper>
  );
}
