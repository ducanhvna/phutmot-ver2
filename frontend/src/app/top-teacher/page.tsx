"use client";

import React, { useState } from "react";
import { useGetIdentity } from "@refinedev/core";
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  Badge,
  Card,
  CardContent,
  Chip,
  Button,
} from "@mui/material";
import { User } from "@api/authApi";
import {
  Notifications as NotificationsIcon,
  CloudUpload as DataUploadIcon,
  MoreHoriz as MoreIcon,
  AssignmentTurnedIn,
  Dashboard,
  TrackChangesOutlined,
  DriveFileRenameOutlineOutlined,
  GradingOutlined,
  AssessmentOutlined,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";

export default function TopTeacherPage() {
  const { data: user } = useGetIdentity<User>();
  const [expanded, setExpanded] = useState(true);
  const router = useRouter();

  // Sample notification data
  const notifications = [
    {
      id: 1,
      content: "テストの再分析が完了しました",
      time: "2025-06-24 14:30",
      read: false,
    },
    {
      id: 2,
      content: "200件のデジタルドリルの学習データを登録しました。",
      time: "2025-06-23 10:15",
      read: true,
    },
    {
      id: 3,
      content: "問題属性診断が完了しました",
      time: "2025-06-22 16:45",
      read: true,
    },
    {
      id: 4,
      content: "テストの採点結果が登録されました",
      time: "2025-06-21 09:30",
      read: false,
    },
  ];

  // Sample scores for histogram
  const sampleScores = [
    65, 72, 78, 75, 82, 85, 89, 91, 68, 72, 77, 81, 86, 90, 95,
  ];

  const buttonData = [
    {
      icon: <TrackChangesOutlined sx={{ fontSize: 42 }} />,
      text: "目標設定",
      backgroundColor: "var(--color-blue)",
      url: "/goals-setup",
    },
    {
      icon: <DriveFileRenameOutlineOutlined sx={{ fontSize: 42 }} />,
      text: "日々の学習記録",
      backgroundColor: "var(--color-green)",
      url: "/daily-progress-teacher",
    },
    {
      icon: <GradingOutlined sx={{ fontSize: 42 }} />,
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
          }}
        />
      ),
      url: "/tests-review",
    },
    {
      icon: <AssessmentOutlined sx={{ fontSize: 42 }} />,
      text: "学習全体の振り返り",
      backgroundColor: "var(--color-orange)",
      url: "/learning-overview",
    },
  ];

  const listButtonData = [
    {
      icon: <AssignmentTurnedIn sx={{ fontSize: 24 }} />,
      text: "採点 - RealtenDant",
    },
    {
      icon: <Dashboard sx={{ fontSize: 24 }} />,
      text: "総合分析ダッシュボード",
    },
    {
      icon: <DataUploadIcon sx={{ fontSize: 24 }} />,
      text: "学習データ登録",
    },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        minHeight: "calc(100vh - 64px)",
        bgcolor: "var(--color-main)",
        padding: 2,
      }}
    >
      {/* Main Content */}
      <Box sx={{ flex: 1, p: 3 }}>
        {/* Header with maintenance notice */}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            mb: 3,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: "var(--color-gray)",
            borderRadius: 2,
          }}
        >
          <Box>
            <Typography
              variant="body2"
              sx={{ fontWeight: "medium", textAlign: "center" }}
            >
              8/12（月）21時～8/12（火）6時までメンテナンスのためご利用いただけませんのでご了承ください。
              (2025/7/3 9:00)
            </Typography>
          </Box>
        </Paper>

        {/* Main Function Buttons */}
        <Box
          sx={{
            position: { md: "sticky" },
            top: 76,
            zIndex: 10,
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            flexWrap: { xs: "nowrap", sm: "wrap", md: "nowrap" },
            gap: 2,
            mb: 4,
            backgroundColor: "var(--color-main)",
          }}
        >
          {buttonData.map((button, index) => (
            <Button
              onClick={() => router.push(button.url)}
              key={button.text}
              sx={{
                width: { xs: "100%", sm: "calc(50% - 8px)", md: "25%" },
                height: { xs: 100, md: 120 },
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                alignItems: "center",
                justifyContent: { xs: "center" },
                gap: 2,
                p: { xs: 2, md: 4 },
                borderRadius: 2,
                fontWeight: "bold",
                backgroundColor: button.backgroundColor,
                color: "var(--color-white)",
                position: "relative", // Ensure consistent positioning
              }}
            >
              {button.icon}
              <Typography sx={{ fontWeight: "bold" }}>{button.text}</Typography>
              {button.chip}
            </Button>
          ))}
        </Box>

        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 2,
          }}
        >
          {/* Left Sidebar */}
          <Box
            sx={{
              height: "100%",
              width: { xs: "100%", md: "auto" },
            }}
          >
            <List
              sx={{
                display: "flex",
                flexDirection: { xs: "row", md: "column" },
                flexWrap: { xs: "wrap", md: "nowrap" },
                gap: 1,
              }}
            >
              {listButtonData.map((item, index) => (
                <Button
                  key={item.text}
                  sx={{
                    borderRadius: 2,
                    backgroundColor: "var(--color-green)",
                    color: "var(--color-white)",
                    p: { xs: 2, sm: 4, md: 8 },
                    height: { xs: 90, sm: 100, md: 120 },
                    width: { xs: "calc(50% - 4px)", md: "100%" },
                  }}
                >
                  {item.icon}
                  <Typography sx={{ fontWeight: "bold" }}>
                    {item.text}
                  </Typography>
                </Button>
              ))}
            </List>
          </Box>

          {/* Notifications/Timeline Section */}
          <Paper
            elevation={2}
            sx={{
              p: 2,
              borderRadius: 2,
              mb: 3,
              flex: 1,
              width: { xs: "100%", md: "auto" },
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                <NotificationsIcon sx={{ verticalAlign: "middle", mr: 1 }} />
                最近の活動
              </Typography>
              <Typography
                variant="body2"
                color="primary"
                sx={{ cursor: "pointer" }}
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? "折りたたむ" : "すべてを表示"}
              </Typography>
            </Box>

            <List>
              {notifications
                .slice(0, expanded ? notifications.length : 2)
                .map((notification) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      alignItems="flex-start"
                      sx={{
                        bgcolor: notification.read
                          ? "transparent"
                          : "rgba(25, 118, 210, 0.08)",
                        borderRadius: 1,
                        mb: 1,
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                            }}
                          >
                            <Typography
                              variant="body1"
                              sx={{
                                fontWeight: !notification.read
                                  ? "bold"
                                  : "regular",
                              }}
                            >
                              {notification.content}
                            </Typography>
                            {!notification.read && (
                              <Badge color="primary" variant="dot" />
                            )}
                          </Box>
                        }
                        secondary={
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mt: 1 }}
                          >
                            {notification.time}
                          </Typography>
                        }
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" sx={{ ml: 0 }} />
                  </React.Fragment>
                ))}
            </List>
          </Paper>
        </Box>

        {/* Timeline Display Notice */}
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="body2" color="text.secondary">
            タイムライン表示 • スクロール時に順次ローディング
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
