import {
  Paper,
  Typography,
  Box,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Divider,
  TextareaAutosize,
} from "@mui/material";
import { Control, Controller, FieldValues } from "react-hook-form";

type PropsTemplateFeedbackPub = {
  control: Control<FieldValues, {}, FieldValues>;
};

export function TemplateFeedbackPub({ control }: PropsTemplateFeedbackPub) {
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
        評価項目
      </Typography>

      <Box sx={{ mb: 4, flexGrow: 1 }}>
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
          【質問１】今回の授業の内容はよく理解できましたか？
        </Typography>
        <Controller
          control={control}
          name="question1"
          defaultValue=""
          render={({ field }) => (
            <FormControl component="fieldset" sx={{ ml: 2, mt: 2 }}>
              <RadioGroup {...field}>
                <FormControlLabel
                  value="4"
                  control={
                    <Radio
                      sx={{
                        color: "var(--color-green)",
                        "&.Mui-checked": {
                          color: "var(--color-green)",
                        },
                      }}
                    />
                  }
                  label="4 よく理解できた"
                />
                <FormControlLabel
                  value="3"
                  control={
                    <Radio
                      sx={{
                        color: "var(--color-green)",
                        "&.Mui-checked": {
                          color: "var(--color-green)",
                        },
                      }}
                    />
                  }
                  label="3 まあまあ理解できた"
                />
                <FormControlLabel
                  value="2"
                  control={
                    <Radio
                      sx={{
                        color: "var(--color-green)",
                        "&.Mui-checked": {
                          color: "var(--color-green)",
                        },
                      }}
                    />
                  }
                  label="2 あまり理解できなかった"
                />
                <FormControlLabel
                  value="1"
                  control={
                    <Radio
                      sx={{
                        color: "var(--color-green)",
                        "&.Mui-checked": {
                          color: "var(--color-green)",
                        },
                      }}
                    />
                  }
                  label="1 理解できなかった"
                />
              </RadioGroup>
            </FormControl>
          )}
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ flexGrow: 2 }}>
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
          【質問２】質問１の回答の理由や要望など自由に記入してください。
        </Typography>
        <Controller
          control={control}
          name="question2"
          defaultValue=""
          render={({ field }) => (
            <TextareaAutosize
              {...field}
              minRows={7}
              placeholder="ここにコメントを入力してください..."
              style={{
                width: "100%",
                padding: "15px",
                borderRadius: "6px",
                borderColor: "var(--color-green)",
                marginTop: "15px",
                fontFamily: "inherit",
                fontSize: "14px",
                resize: "vertical",
                border: "2px solid var(--color-yellow)",
              }}
            />
          )}
        />
      </Box>
    </Paper>
  );
}
