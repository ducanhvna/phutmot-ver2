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
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import TextField from "@mui/material/TextField";
import QrCodeScannerIcon from "@mui/icons-material/QrCodeScanner";
import { useRouter, useParams } from "next/navigation";
import { getMrpProductionDetail, MrpProduction } from "@/providers/mrp-provider/mrp-production-provider";
import dynamic from "next/dynamic";

// Dùng dynamic import để tránh SSR lỗi với window
const QrReader = dynamic(() => import("react-qr-reader").then(mod => mod.QrReader), { ssr: false });

const MrpProductionDetailPage: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const productionId = params.id as string;

  const [production, setProduction] = useState<MrpProduction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [qrDialogOpen, setQrDialogOpen] = useState(false);
  const [qrScanValue, setQrScanValue] = useState("");
  const [selectedWorkorderId, setSelectedWorkorderId] = useState<number | null>(null);
  const [workorderUserDraft, setWorkorderUserDraft] = useState<Record<number, any[]>>({});
  const [showSave, setShowSave] = useState<Record<number, boolean>>({});
  // Lưu trạng thái quyền camera, kiểm tra khi mở dialog. Nếu đã cấp quyền thì lần sau không cần xin lại, nếu chưa cấp sẽ báo lỗi rõ ràng.
  const [cameraPermission, setCameraPermission] = useState<boolean | null>(null);

  useEffect(() => {
    if (!productionId) return;
    getMrpProductionDetail(Number(productionId))
      .then((data) => setProduction(data))
      .catch(() => setError("Lỗi tải chi tiết lệnh sản xuất"))
      .finally(() => setLoading(false));
  }, [productionId]);

  // Khi mở dialog, kiểm tra quyền camera
  const handleOpenQrDialog = async (workorderId: number) => {
    setSelectedWorkorderId(workorderId);
    setQrDialogOpen(true);
    setQrScanValue("");
    // Kiểm tra quyền camera nếu chưa kiểm tra
    if (navigator && navigator.permissions) {
      try {
        const result = await navigator.permissions.query({ name: "camera" as PermissionName });
        setCameraPermission(result.state === "granted");
        result.onchange = () => setCameraPermission(result.state === "granted");
      } catch {
        setCameraPermission(null); // Không hỗ trợ Permissions API
      }
    }
  };
  const handleCloseQrDialog = () => {
    setQrDialogOpen(false);
    setQrScanValue("");
  };
  // Xử lý khi quét QR xong (giả lập bằng nhập text, thực tế dùng QR scanner component)
  const handleQrScan = () => {
    if (!qrScanValue) return;
    let userObj: any = null;
    try {
      const emp = JSON.parse(qrScanValue);
      if (emp && emp.user_detail && emp.user_detail.id && emp.user_detail.name) {
        userObj = emp.user_detail;
      }
    } catch (e) {
      setError("QR không hợp lệ hoặc không đúng định dạng JSON");
      return;
    }
    if (userObj && selectedWorkorderId !== null) {
      setWorkorderUserDraft((prev: Record<number, any[]>) => {
        const prevList = prev[selectedWorkorderId] || production?.workorders?.find((w: any) => w.id === selectedWorkorderId)?.working_user_details || [];
        // Không thêm trùng user
        if (prevList.some((u: any) => u.id === userObj.id)) return prev;
        return { ...prev, [selectedWorkorderId]: [...prevList, userObj] };
      });
      setShowSave((prev: Record<number, boolean>) => ({ ...prev, [selectedWorkorderId!]: true }));
    }
    setQrScanValue("");
  };
  // Lưu danh sách user cho công đoạn
  const handleSaveUsers = (workorderId: number) => {
    // TODO: Gọi API cập nhật danh sách user cho công đoạn này
    setShowSave((prev) => ({ ...prev, [workorderId]: false }));
  };

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
                <Typography component="span" fontWeight="bold">Trạng thái:</Typography> {production.state || "-"}
              </Typography>
              <Typography>
                <Typography component="span" fontWeight="bold">Sản phẩm:</Typography> {production.product_id && Array.isArray(production.product_id) ? production.product_id[1] : production.product_id || "-"}
              </Typography>
              <Typography>
                <Typography component="span" fontWeight="bold">Số lượng:</Typography> {production.product_qty ?? "-"}
              </Typography>
              <Typography>
                <Typography component="span" fontWeight="bold">Ngày bắt đầu:</Typography> {production.date_start || "-"}
              </Typography>
              <Typography>
                <Typography component="span" fontWeight="bold">Ngày kết thúc:</Typography> {production.date_finished || "-"}
              </Typography>
            </Stack>
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Bảng công đoạn (Hoạt động)
            </Typography>
            {production.workorders && production.workorders.length > 0 ? (
              <Box>
                {production.workorders.map((wo: any) => {
                  const draftUsers = workorderUserDraft[wo.id] || wo.working_user_details || [];
                  return (
                    <Paper key={wo.id} sx={{ p: 2, mb: 2, bgcolor: "#f5f5f5" }}>
                      <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {wo.name} (ID: {wo.id})
                        </Typography>
                        <Typography color="text.secondary">Trạng thái: {wo.state || "-"}</Typography>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<QrCodeScannerIcon />}
                          sx={{ ml: 2 }}
                          onClick={() => handleOpenQrDialog(wo.id)}
                        >
                          Thêm user
                        </Button>
                        {showSave[wo.id] && (
                          <Button
                            variant="contained"
                            color="success"
                            size="small"
                            sx={{ ml: 1 }}
                            onClick={() => handleSaveUsers(wo.id)}
                          >
                            Lưu
                          </Button>
                        )}
                      </Stack>
                      <Typography mb={1}>
                        <Typography component="span" fontWeight="bold">Thời gian:</Typography> {wo.date_start || "-"} - {wo.date_finished || "-"}
                      </Typography>
                      <Typography mb={1}>
                        <Typography component="span" fontWeight="bold">Tiến độ:</Typography> {wo.progress ?? "-"}%
                      </Typography>
                      <Typography mb={1}>
                        <Typography component="span" fontWeight="bold">Người dùng đang tham gia:</Typography>
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        {draftUsers.length > 0 ? (
                          draftUsers.map((user: any) => (
                            <Chip key={user.id} label={user.name} color="primary" variant="outlined" />
                          ))
                        ) : (
                          <Typography color="text.secondary">Không có user nào</Typography>
                        )}
                      </Stack>
                    </Paper>
                  );
                })}
                {/* Dialog quét QR */}
                <Dialog open={qrDialogOpen} onClose={handleCloseQrDialog}>
                  <DialogTitle>Quét QR nhân viên để thêm user vào công đoạn</DialogTitle>
                  <DialogContent>
                    {cameraPermission === false && (
                      <Typography color="error" mb={2}>
                        Bạn cần cho phép truy cập camera để quét QR. Hãy kiểm tra lại quyền trong trình duyệt!
                      </Typography>
                    )}
                    <Box sx={{ width: "100%" }}>
                      <QrReader
                        constraints={{ facingMode: "environment" }}
                        onResult={(result: any, error: any) => {
                          if (result) {
                            try {
                              const text = result.getText();
                              if (text && text !== qrScanValue) {
                                setQrScanValue(text);
                                setError(null);
                                setTimeout(() => {
                                  handleQrScan();
                                  handleCloseQrDialog();
                                }, 200);
                              }
                            } catch (e) {
                              setError("QR không hợp lệ hoặc không đúng định dạng JSON");
                            }
                          }
                          if (error && error.name === "NotAllowedError") {
                            setCameraPermission(false);
                            setError("Bạn cần cho phép truy cập camera để quét QR");
                          } else if (error && error.name === "NotFoundError") {
                            setError("Không tìm thấy thiết bị camera trên máy của bạn");
                          } else if (error && error.name) {
                            setError(`Lỗi camera: ${error.name}`);
                          }
                        }}
                      />
                    </Box>
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={handleCloseQrDialog} color="primary">
                      Đóng
                    </Button>
                  </DialogActions>
                </Dialog>
              </Box>
            ) : (
              <Typography color="text.secondary">Không có công đoạn nào cho lệnh sản xuất này.</Typography>
            )}
          </Box>
        )}
      </Paper>
    </Show>
  );
};

export default MrpProductionDetailPage;
