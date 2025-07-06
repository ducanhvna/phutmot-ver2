"use client";

import React, { useState } from "react";
import {
  Avatar,
  Box,
  Typography,
  Paper,
  IconButton,
  Card,
  CardContent,
  Chip,
  Button,
} from "@mui/material";
import {
  Notifications as NotificationsIcon,
  AssignmentTurnedIn,
  Book as LearningRecordIcon,
  Book as BookIcon,
  Assessment as TestReviewIcon,
  TrendingUp as LearningOverviewIcon,
  MoreHoriz as MoreIcon,
  EmojiEvents as TrophyIcon,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import Notifications from "@components/notifications";

export default function TopStudentPage() {
  const [expanded, setExpanded] = useState(true);
  const router = useRouter();

  // Sample notification data
  const notifications = [
    {
      id: 1,
      content: "テストの再分析が完了しました",
      time: "2025-06-24 14:30",
      read: false,
      type: "test" as "test",
      actionText: "確認する",
      actionUrl: "/test-analysis",
      isNew: true,
    },
    {
      id: 2,
      content: "200件のデジタルドリルの学習データを登録しました。",
      time: "2025-06-23 10:15",
      read: true,
      type: "learning" as "learning",
    },
    {
      id: 3,
      content: "問題属性診断が完了しました",
      time: "2025-06-22 16:45",
      read: true,
      type: "stats" as "stats",
      actionText: "詳細を見る",
      actionUrl: "/problem-analysis",
    },
    {
      id: 4,
      content: "テストの採点結果が登録されました",
      time: "2025-06-21 09:30",
      read: false,
      type: "task" as "task",
      actionText: "確認する",
      actionUrl: "/test-results",
    },
  ];

  // Calculate unread notifications count
  const unreadCount = notifications.filter(
    (notification) => !notification.read
  ).length;

  // Sample scores for histogram
  const sampleScores = [
    65, 72, 78, 75, 82, 85, 89, 91, 68, 72, 77, 81, 86, 90, 95,
  ];

  // Button data for main functions
  const buttonData = [
    {
      icon: <AssignmentTurnedIn sx={{ fontSize: 42, mb: 0.5 }} />,
      text: "目標設定（準備中）",
      backgroundColor: "var(--color-blue)",
      url: "/goals-setup-student",
    },
    {
      icon: <LearningRecordIcon sx={{ fontSize: 42, mb: 0.5 }} />,
      text: "日々の学習記録",
      backgroundColor: "var(--color-green)",
      url: "/daily-progress-student",
    },
    {
      icon: <TestReviewIcon sx={{ fontSize: 42, mb: 0.5 }} />,
      text: "テスト振り返り",
      backgroundColor: "var(--color-purple)",
      chip: (
        <Chip
          label="New"
          color="error"
          size="small"
          sx={{
            position: "absolute",
            top: 12,
            right: 12,
            fontWeight: "bold",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(217, 83, 75, 0.4)",
          }}
        />
      ),
      url: "/tests-review-student",
    },
    {
      icon: <LearningOverviewIcon sx={{ fontSize: 42, mb: 0.5 }} />,
      text: "学習全体の振り返り",
      backgroundColor: "var(--color-orange)",
      url: "/learning-overview-student",
    },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        minHeight: "calc(100vh - 64px)",
        bgcolor: "var(--color-main)",
        padding: { xs: 1, sm: 2 },
      }}
    >
      {/* Main Content */}
      <Box sx={{ flex: 1, p: { xs: 1.5, sm: 3 } }}>
        {/* Header with maintenance notice */}
        <Box
          sx={{
            p: { xs: 2, sm: 2.5 },
            mb: "27px",
            background: "var(--color-gray)",
            borderRadius: 3,
            overflow: "hidden",
            textAlign: "center",
          }}
        >
          <Typography
            variant="body1"
            sx={{
              fontWeight: "medium",
              color: "var(--color-text-black))",
              textShadow: "0 1px 2px rgba(0,0,0,0.1)",
              fontSize: { xs: "0.85rem", sm: "1rem" },
              lineHeight: 1.5,
              textAlign: "center",
            }}
          >
            8/12（月）21時～8/12（火）6時までメンテナンスのためご利用いただけませんのでご了承ください。
            (2025/7/3 9:00)
          </Typography>
        </Box>

        {/* Main Function Buttons */}
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            gap: { xs: 2, md: 3 },
            mb: 5,
          }}
        >
          {buttonData.map((button, index) => (
            <Button
              onClick={() => router.push(button.url)}
              key={button.text}
              sx={{
                width: { xs: "100%" },
                height: { xs: 110, sm: 130 },
                display: "flex",
                flexDirection: "column",
                gap: 1.5,
                p: 2.5,
                borderRadius: 4,
                fontWeight: "bold",
                boxShadow: "0 6px 20px rgba(23, 160, 152, 0.2)",
                backgroundColor: button.backgroundColor,
                color: "var(--color-white)",
                position: "relative",
              }}
            >
              {button.icon}
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: "bold",
                  fontSize: { xs: "0.9rem", sm: "1.05rem" },
                  textAlign: "center",
                }}
              >
                {button.text}
              </Typography>
              {button.chip}
            </Button>
          ))}
        </Box>

        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 3,
          }}
        >
          {/* Left Sidebar */}
          <Box
            width={{ xs: "100%", md: 340 }}
            minWidth={{ xs: "unset", md: 260 }}
            maxWidth={{ xs: "100%", md: 400 }}
            flexShrink={0}
            display="flex"
            flexDirection="column"
            gap={4}
            mb={{ xs: 4, md: 0 }}
            sx={{
              position: { md: "sticky" },
              top: 76,
              zIndex: 10,
              display: "flex",
              gap: 2,
              backgroundColor: "var(--color-main)",
            }}
          >
            {/* 目標 エリア */}
            <Paper
              elevation={2}
              sx={{
                p: { xs: 2, sm: 3 },
                borderRadius: 3,
                background:
                  "linear-gradient(145deg, var(--color-white), var(--color-main-secondary))",
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
                "&:hover": {
                  transform: { sm: "translateY(-5px)" },
                  boxShadow: "0 12px 20px rgba(0, 0, 0, 0.1)",
                },
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  mb: 2,
                }}
              >
                <TrophyIcon
                  sx={{
                    color: "var(--color-yellow)",
                    fontSize: { xs: 24, sm: 28 },
                  }}
                />
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  gutterBottom
                  sx={{
                    m: 0,
                    fontSize: { xs: "1.15rem", sm: "1.5rem" },
                  }}
                >
                  目標
                </Typography>
              </Box>
              <Box
                display="flex"
                alignItems="center"
                gap={2}
                mb={2}
                sx={{
                  background:
                    "linear-gradient(145deg, var(--color-blue-secondary), var(--color-main))",
                  borderRadius: 2,
                  p: { xs: 1.5, sm: 2 },
                }}
              >
                <Avatar
                  sx={{
                    width: { xs: 45, sm: 56 },
                    height: { xs: 45, sm: 56 },
                    bgcolor: "var(--color-blue)",
                    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.15)",
                  }}
                />
                <Typography
                  sx={{
                    fontWeight: "medium",
                    color: "#333",
                    fontSize: { xs: "0.85rem", sm: "1rem" },
                  }}
                >
                  テキスト or 画像 サムネイル
                </Typography>
              </Box>
              <Typography
                variant="body1"
                sx={{
                  fontWeight: "bold",
                  color: "var(--color-blue)",
                  p: { xs: 1, sm: 1.5 },
                  bgcolor: "rgba(169, 209, 238, 0.2)",
                  borderRadius: 1.5,
                  textAlign: "center",
                  fontSize: { xs: "0.85rem", sm: "1rem" },
                }}
              >
                年間 目標表示エリア
              </Typography>
            </Paper>

            {/* まなびのとびら エリア */}
            <Paper
              elevation={2}
              sx={{
                p: { xs: 2, sm: 3 },
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                borderRadius: 3,
                background:
                  "linear-gradient(145deg, var(--color-white), var(--color-main-secondary))",
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
                "&:hover": {
                  transform: { sm: "translateY(-5px)" },
                  boxShadow: "0 12px 20px rgba(0, 0, 0, 0.1)",
                },
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  mb: 2,
                }}
              >
                <BookIcon
                  sx={{
                    color: "var(--color-green)",
                    fontSize: { xs: 24, sm: 28 },
                  }}
                />
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  gutterBottom
                  sx={{
                    m: 0,
                    fontSize: { xs: "1.15rem", sm: "1.5rem" },
                  }}
                >
                  まなびのとびら
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  color: "#555",
                  mb: 2,
                  p: { xs: 1, sm: 1.5 },
                  bgcolor: "rgba(23, 160, 152, 0.1)",
                  borderRadius: 1.5,
                  width: "100%",
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
                }}
              >
                バナーをデザインしてボタン押下でモーダルでコンテンツ表示
                (なければ非表示)
              </Typography>
              <Button
                sx={{
                  borderRadius: 8,
                  px: { xs: 2, sm: 3 },
                  py: { xs: 0.75, sm: 1 },
                  fontWeight: "bold",
                  fontSize: { xs: "0.85rem", sm: "0.9rem" },
                  boxShadow: "0 4px 8px rgba(23, 160, 152, 0.25)",
                  transition: "transform 0.2s ease, box-shadow 0.2s ease",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: "0 6px 12px rgba(23, 160, 152, 0.3)",
                  },
                }}
              >
                コンテンツを開く
              </Button>
            </Paper>
          </Box>

          {/* Notifications/Timeline Section */}
          <Box
            sx={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              p: { xs: 2, sm: 3 },
              borderRadius: 3,
              mb: 4,
              background:
                "linear-gradient(145deg, var(--color-white), var(--color-main-secondary))",
              boxShadow: "0 10px 25px rgba(149, 157, 165, 0.2)",
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                justifyContent: { sm: "space-between" },
                alignItems: { xs: "flex-start", sm: "center" },
                mb: 3,
                pb: 1.5,
                gap: { xs: 1, sm: 0 },
                borderBottom: "2px solid var(--color-main)",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <NotificationsIcon
                  sx={{
                    verticalAlign: "middle",
                    mr: 1.5,
                    fontSize: { xs: 24, sm: 28 },
                    color: "var(--color-blue)",
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: "bold",
                    background:
                      "linear-gradient(90deg, var(--color-blue), var(--color-purple))",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    fontSize: { xs: "1.1rem", sm: "1.2rem", md: "1.3rem" },
                  }}
                >
                  最近の活動
                </Typography>
              </Box>
              {/* Removed redundant expand/collapse text since the Notifications component now handles this */}
            </Box>

            <Notifications
              notifications={notifications}
              expanded={expanded}
              onToggleExpand={() => setExpanded(!expanded)}
              title="最近の活動"
              unreadCount={unreadCount}
            />
            {/* Histogram Card */}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
