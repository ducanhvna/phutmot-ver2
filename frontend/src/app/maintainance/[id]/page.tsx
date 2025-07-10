"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
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
  getAllEquipments,
  Equipment,
} from "@/providers/maintainance-provider/maintainance-provider";

const EquipmentDetailPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const equipmentId = params.id as string;

  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!equipmentId) return;
    getAllEquipments()
      .then((data) => {
        const found = data.find((eq) => String(eq.id) === equipmentId);
        setEquipment(found || null);
      })
      .catch(() => setError("Lỗi tải thông tin thiết bị"))
      .finally(() => setLoading(false));
  }, [equipmentId]);

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
      resource="equipments"
      goBack={<BackButton />}
      breadcrumb={
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          aria-label="breadcrumb"
        >
          <Link
            color="inherit"
            href="/maintainance"
            onClick={(e) => {
              e.preventDefault();
              router.push("/maintainance");
            }}
          >
            Thiết bị
          </Link>
          <Typography color="text.primary">Chi tiết</Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          Chi tiết thiết bị
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
          <Typography>Đang tải thông tin thiết bị...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : !equipment ? (
          <Typography>Không tìm thấy thiết bị.</Typography>
        ) : (
          <Box>
            <Stack direction="row" alignItems="center" spacing={2} mb={2}>
              <DescriptionIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                {equipment.name}
              </Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              <Typography>
                <strong>ID:</strong> {equipment.id}
              </Typography>
              <Typography>
                <strong>Số serial:</strong> {equipment.serial_no || "-"}
              </Typography>
              <Typography>
                <strong>Phòng ban:</strong>{" "}
                {equipment.department_id
                  ? Array.isArray(equipment.department_id)
                    ? equipment.department_id[1]
                    : equipment.department_id
                  : "-"}
              </Typography>
              <Typography>
                <strong>Nhân viên được giao:</strong>{" "}
                {equipment.employee_id
                  ? Array.isArray(equipment.employee_id)
                    ? equipment.employee_id[1]
                    : equipment.employee_id
                  : "-"}
              </Typography>
              <Typography>
                <strong>Ngày hết hạn bảo hành:</strong>{" "}
                {equipment.warranty_date || "-"}
              </Typography>
              <Typography>
                <strong>Ghi chú:</strong> {equipment.note || "-"}
              </Typography>
              {/* Thêm các trường khác nếu cần */}
            </Stack>
          </Box>
        )}
      </Paper>
    </Show>
  );
};

export default EquipmentDetailPage;
