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
  Chip,
} from "@mui/material";
import { Show } from "@refinedev/mui";
import DescriptionIcon from "@mui/icons-material/Description";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AddIcon from "@mui/icons-material/Add";
import { useRouter, useParams } from "next/navigation";
import { getMrpProductionDetail, MrpProduction } from "@/providers/mrp-provider/mrp-production-provider";

const MrpProductionDetailPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const productionId = params.id as string;

  const [production, setProduction] = useState<MrpProduction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productionId) return;
    getMrpProductionDetail(Number(productionId))
      .then((data) => setProduction(data))
      .catch(() => setError("Lỗi tải chi tiết lệnh sản xuất"))
      .finally(() => setLoading(false));
  }, [productionId]);

  return (
    <Show
      resource="mrp-productions"
      goBack={false}
      breadcrumb={
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb">
          <Link
            color="inherit"
            href="/mrp-productions"
            onClick={(e) => {
              e.preventDefault();
              router.push("/mrp-productions");
            }}
          >
            Lệnh sản xuất
          </Link>
          <Typography color="text.primary">Chi tiết</Typography>
        </Breadcrumbs>
      }
      title={
        <Typography variant="h5" fontWeight="700">
          Chi tiết lệnh sản xuất
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      <Paper elevation={2} sx={{ p: 3, borderRadius: "10px", bgcolor: "var(--color-white)" }}>
        {loading ? (
          <Typography>Đang tải chi tiết lệnh sản xuất...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : !production ? (
          <Typography>Không tìm thấy lệnh sản xuất.</Typography>
        ) : (
          <Box>
            <Stack direction="row" alignItems="center" spacing={2} mb={2}>
              <DescriptionIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                {production.name} (ID: {production.id})
              </Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              <Typography>
                <b>Trạng thái:</b> {production.state || "-"}
              </Typography>
              <Typography>
                <b>Sản phẩm:</b> {production.product_id && Array.isArray(production.product_id) ? production.product_id[1] : production.product_id || "-"}
              </Typography>
              <Typography>
                <b>Số lượng:</b> {production.product_qty ?? "-"}
              </Typography>
              <Typography>
                <b>Ngày bắt đầu:</b> {production.date_start || "-"}
              </Typography>
              <Typography>
                <b>Ngày kết thúc:</b> {production.date_finished || "-"}
              </Typography>
            </Stack>
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Bảng công đoạn (Hoạt động)
            </Typography>
            {production.workorders && production.workorders.length > 0 ? (
              <Box>
                {production.workorders.map((wo: any) => (
                  <Paper key={wo.id} sx={{ p: 2, mb: 2, bgcolor: "#f5f5f5" }}>
                    <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {wo.name} (ID: {wo.id})
                      </Typography>
                      <Typography color="text.secondary">Trạng thái: {wo.state || "-"}</Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<AddIcon />}
                        sx={{ ml: 2 }}
                        onClick={() => {
                          // TODO: Xử lý thêm user vào công đoạn này
                        }}
                      >
                        Thêm user
                      </Button>
                    </Stack>
                    <Typography mb={1}>
                      <b>Thời gian:</b> {wo.date_start || "-"} - {wo.date_finished || "-"}
                    </Typography>
                    <Typography mb={1}>
                      <b>Tiến độ:</b> {wo.progress ?? "-"}%
                    </Typography>
                    <Typography mb={1}>
                      <b>Người dùng đang tham gia:</b>
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {wo.working_user_details && wo.working_user_details.length > 0 ? (
                        wo.working_user_details.map((user: any) => (
                          <Chip key={user.id} label={user.name} color="primary" variant="outlined" />
                        ))
                      ) : (
                        <Typography color="text.secondary">Không có user nào</Typography>
                      )}
                    </Stack>
                  </Paper>
                ))}
              </Box>
            ) : (
              <Typography>Không có công đoạn nào.</Typography>
            )}
          </Box>
        )}
      </Paper>
    </Show>
  );
};

export default MrpProductionDetailPage;
