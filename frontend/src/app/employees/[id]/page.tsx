"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Divider,
  Breadcrumbs,
  Link,
  Stack,
} from "@mui/material";
import { Show } from "@refinedev/mui";
import DescriptionIcon from "@mui/icons-material/Description";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useRouter, useParams } from "next/navigation";
import { useBack } from "@refinedev/core";
import {
  getEmployeeById,
  Employee,
} from "@/providers/employee-provider/employee-provider";
import QRCode from "react-qr-code";

const EmployeeDetailPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const empId = params.id as string;

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!empId) return;
    getEmployeeById(Number(empId))
      .then((data) => setEmployee(data))
      .catch(() => setError("Lỗi tải thông tin nhân viên"))
      .finally(() => setLoading(false));
  }, [empId]);

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
      resource="employees"
      goBack={<BackButton />}
      breadcrumb={
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          aria-label="breadcrumb"
        >
          <Link
            color="inherit"
            href="/employees"
            onClick={(e) => {
              e.preventDefault();
              router.push("/employees");
            }}
          >
            Nhân viên
          </Link>
          <Typography color="text.primary">Chi tiết</Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          Chi tiết nhân viên
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      <Paper
        elevation={2}
        sx={{ p: 3, borderRadius: "10px", bgcolor: "var(--color-white)" }}
      >
        {loading ? (
          <Typography>Đang tải thông tin nhân viên...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : !employee ? (
          <Typography>Không tìm thấy nhân viên.</Typography>
        ) : (
          <Box>
            <Stack direction="row" alignItems="center" spacing={2} mb={2}>
              <DescriptionIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                {employee.name}
              </Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              <Typography>
                <span style={{ fontWeight: "bold" }}>ID:</span> {employee.id}
              </Typography>
              <Typography>
                <span style={{ fontWeight: "bold" }}>Email:</span>{" "}
                {employee.work_email || "-"}
              </Typography>
              <Typography>
                <span style={{ fontWeight: "bold" }}>Điện thoại:</span>{" "}
                {employee.work_phone || "-"}
              </Typography>
              <Typography>
                <span style={{ fontWeight: "bold" }}>Chức vụ:</span>{" "}
                {employee.job_title || "-"}
              </Typography>
              <Typography>
                <span style={{ fontWeight: "bold" }}>Phòng ban:</span>{" "}
                {employee.department_id
                  ? Array.isArray(employee.department_id)
                    ? employee.department_id[1]
                    : employee.department_id
                  : "-"}
              </Typography>
              <Typography>
                <span style={{ fontWeight: "bold" }}>User ID:</span>{" "}
                {employee.user_id
                  ? Array.isArray(employee.user_id)
                    ? employee.user_id[0]
                    : employee.user_id
                  : "-"}
              </Typography>
              {employee.user_detail && (
                <Box sx={{ pl: 2, borderLeft: "3px solid #1976d2", mt: 1 }}>
                  <Typography
                    variant="subtitle1"
                    fontWeight="bold"
                    color="primary"
                  >
                    Thông tin User
                  </Typography>
                  <Typography>
                    <span style={{ fontWeight: "bold" }}>Tên user:</span>{" "}
                    {employee.user_detail.name}
                  </Typography>
                  <Typography>
                    <span style={{ fontWeight: "bold" }}>Email:</span>{" "}
                    {employee.user_detail.email || "-"}
                  </Typography>
                  <Typography>
                    <span style={{ fontWeight: "bold" }}>Login:</span>{" "}
                    {employee.user_detail.login || "-"}
                  </Typography>
                  <Typography>
                    <span style={{ fontWeight: "bold" }}>Công ty:</span>{" "}
                    {employee.user_detail.company_id
                      ? Array.isArray(employee.user_detail.company_id)
                        ? employee.user_detail.company_id[1]
                        : employee.user_detail.company_id
                      : "-"}
                  </Typography>
                  <Typography>
                    <span style={{ fontWeight: "bold" }}>Kích hoạt:</span>{" "}
                    {employee.user_detail.active ? "Có" : "Không"}
                  </Typography>
                </Box>
              )}
            </Stack>
            <Divider sx={{ my: 3 }} />
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              gap={2}
            >
              <Typography variant="subtitle1" fontWeight="bold">
                Mã QR thông tin nhân viên
              </Typography>
              <QRCode
                value={JSON.stringify(
                  { ...employee, user_detail: employee.user_detail },
                  null,
                  2
                )}
                size={200}
              />
            </Box>
          </Box>
        )}
      </Paper>
    </Show>
  );
};

export default EmployeeDetailPage;
