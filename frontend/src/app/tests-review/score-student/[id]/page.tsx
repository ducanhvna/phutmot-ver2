"use client";

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Divider,
  Stack,
  Breadcrumbs,
  Tooltip,
  Link,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import AssessmentIcon from '@mui/icons-material/Assessment';
import EmojiObjectsIcon from '@mui/icons-material/EmojiObjects';
import { Show } from '@refinedev/mui';
import { useBack } from '@refinedev/core';

// Mock student score data
const studentScoreData = {
  id: "1",
  testName: "２学期中間テスト",
  year: "2025",
  subject: "英語",
  grade: "２年",
  classRoom: "３組",
  studentNumber: "１番",
  studentName: "氏名", // Will be replaced with actual name in real implementation
  score: 82,
  correctRate: 85.4,
  knowledgeSkillRate: 90,
  thinkingJudgmentExpressionRate: 45,
  carelessMistakes: 2,
  standardScore: 58.4,
  comprehensionRank: "B",
  comment: "理解度ランクBです。知識技能の問題はよくできています。Aランクにするには、応用問題にも十分時間をかけて取り組みましょう。"
};

const ScoreStudentPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const studentId = params.id as string;

  // In a real app, this would fetch the student data based on the studentId
  // For now, we'll just log that we received the ID
  console.log(`Displaying score details for student with ID: ${studentId}`);

  // We would normally fetch real data here based on the studentId
  // const [studentData, setStudentData] = useState(null);
  // useEffect(() => {
  //   const fetchStudentData = async () => {
  //     // API call to get student data
  //     const data = await fetchStudentById(studentId);
  //     setStudentData(data);
  //   };
  //   fetchStudentData();
  // }, [studentId]);

  const BackButton = () => {
    const goBack = useBack();
    return (
      <IconButton onClick={goBack}>
        <ArrowBackIcon />
      </IconButton>
    );
  };

  return (
    <Show
      resource="score-student"
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
          <Link
            color="inherit"
            href={`/tests-review/${studentScoreData.id}`}
            onClick={(e) => {
              e.preventDefault();
              router.push(`/tests-review/${studentScoreData.id}`);
            }}
          >
            テスト詳細
          </Link>
          <Typography
            color="text.primary"
            sx={{ display: "flex", alignItems: "center" }}
          >
            教科別個票
          </Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          教科別個票
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      {/* Header section */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
        }}
      >
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="h6"
            sx={{
              display: "flex",
              alignItems: "center",
              color: "var(--color-green)",
            }}
          >
            <AssessmentIcon sx={{ mr: 1 }} />
            生徒の個票情報
          </Typography>

          <Typography variant="h5" fontWeight="bold" sx={{ mt: 2 }}>
            {studentScoreData.year}年度 {studentScoreData.testName} {studentScoreData.subject}
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box>
          <Stack direction="row" spacing={4} flexWrap="wrap" sx={{ mb: 2 }}>
            <Typography variant="body1">
              <strong>学年・クラス:</strong> {studentScoreData.grade}{studentScoreData.classRoom}
            </Typography>
            <Typography variant="body1">
              <strong>出席番号:</strong> {studentScoreData.studentNumber}
            </Typography>
            <Typography variant="body1">
              <strong>氏名:</strong> {studentScoreData.studentName}
            </Typography>
          </Stack>
        </Box>
      </Paper>

      {/* Score details section */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
        }}
      >
        <Typography
          variant="h6"
          sx={{
            mb: 2,
            display: "flex",
            alignItems: "center",
            color: "var(--color-blue)",
            fontWeight: "bold",
          }}
        >
          <AssessmentIcon sx={{ mr: 1 }} />
          成績情報
        </Typography>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {/* Main score */}
          <Box sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            mb: 2
          }}>
            <Typography variant="h6" fontWeight="bold" sx={{ color: "var(--color-blue)" }}>
              得点
            </Typography>
            <Typography
              variant="h3"
              sx={{
                color: "var(--color-blue)",
                fontWeight: "bold",
                display: "flex",
                alignItems: "baseline"
              }}
            >
              {studentScoreData.score}
              <Typography component="span" variant="h5" sx={{ ml: 1 }}>点</Typography>
            </Typography>
          </Box>

          {/* Score details */}
          <Box sx={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-around",
            gap: 2,
            mt: 2
          }}>
            <ScoreDetailCard
              title="正答率"
              value={`${studentScoreData.correctRate}%`}
              color="var(--color-green)"
            />

            <ScoreDetailCard
              title="知識・技能"
              value={`${studentScoreData.knowledgeSkillRate}%`}
              color="var(--color-blue)"
            />

            <ScoreDetailCard
              title="思考・判断・表現"
              value={`${studentScoreData.thinkingJudgmentExpressionRate}%`}
              color="var(--color-purple)"
            />
          </Box>

          <Box sx={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-around",
            gap: 2,
            mt: 2
          }}>
            <ScoreDetailCard
              title="ケアレスミスかも"
              value={`${studentScoreData.carelessMistakes}問`}
              color="var(--color-orange)"
            />

            <ScoreDetailCard
              title="偏差値"
              value={studentScoreData.standardScore.toString()}
              color="var(--color-blue)"
            />

            <ScoreDetailCard
              title="理解度ランク"
              value={studentScoreData.comprehensionRank}
              color="var(--color-yellow)"
            />
          </Box>
        </Box>
      </Paper>

      {/* Commentary section */}
      <Paper
        elevation={2}
        sx={{
          p: 3,
          borderRadius: "10px",
          bgcolor: "var(--color-white)",
        }}
      >
        <Typography
          variant="h6"
          sx={{
            mb: 2,
            display: "flex",
            alignItems: "center",
            color: "var(--color-yellow)",
            fontWeight: "bold",
          }}
        >
          <EmojiObjectsIcon sx={{ mr: 1 }} />
          学習アドバイス
        </Typography>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{
          p: 2,
          bgcolor: "var(--color-main-secondary)",
          borderRadius: "8px",
          border: "1px solid var(--color-gray)"
        }}>
          <Typography variant="body1" sx={{ whiteSpace: "pre-line", lineHeight: "1.8" }}>
            {studentScoreData.comment}
          </Typography>
        </Box>
      </Paper>
    </Show>
  );
};

// Helper component for score detail cards
interface ScoreDetailCardProps {
  title: string;
  value: string;
  color: string;
}

const ScoreDetailCard: React.FC<ScoreDetailCardProps> = ({ title, value, color }) => {
  return (
    <Box sx={{
      width: { xs: '100%', sm: '30%', md: '30%' },
      minWidth: '200px',
      p: 2,
      borderRadius: "8px",
      border: `1px solid ${color}`,
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 1,
      textAlign: 'center',
      backgroundColor: 'rgba(255, 255, 255, 0.8)'
    }}>
      <Typography variant="subtitle1" fontWeight="bold" sx={{ color }}>
        {title}
      </Typography>
      <Typography variant="h5" fontWeight="bold" sx={{ color }}>
        {value}
      </Typography>
    </Box>
  );
};

export default ScoreStudentPage;
