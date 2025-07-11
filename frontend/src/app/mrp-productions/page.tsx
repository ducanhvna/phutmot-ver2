"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Typography,
  Box,
  Paper,
  Button,
  IconButton,
  Tooltip,
} from "@mui/material";
import { Show } from "@refinedev/mui";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import SharedTable from "@components/shared-table";
import {
  getAllMrpProductions,
  MrpProduction,
} from "@/providers/mrp-provider/mrp-production-provider";

export default function MrpProductions() {
  const [productions, setProductions] = useState<MrpProduction[]>([]);
  const router = useRouter();

  useEffect(() => {
    async function fetchProductions() {
      const data = await getAllMrpProductions();
      setProductions(data);
    }
    fetchProductions();
  }, []);

  const handleDelete = (id: number) => {
    console.log(`Delete production with ID: ${id}`);
    // Implement delete functionality
  };

  const handleNewRegistration = () => {
    // Điều hướng đến trang tạo mới lệnh sản xuất nếu có
    // router.push("/mrp-productions/create");
  };

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          Danh sách lệnh sản xuất
        </Typography>
      }
      wrapperProps={{
        sx: {
          backgroundColor: "var(--color-main)",
          padding: { xs: 2, md: 4 },
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          gap: 3,
        }}
      >
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 3 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleNewRegistration}
              sx={{
                backgroundColor: "var(--color-green)",
                "&:hover": {
                  backgroundColor: "var(--color-green)",
                  opacity: 0.9,
                },
              }}
            >
              Tạo lệnh sản xuất mới
            </Button>
          </Box>

          <Paper
            elevation={2}
            sx={{ borderRadius: "10px", overflow: "hidden", mb: 3 }}
          >
            <SharedTable
              dataSource={productions}
              themeColor="var(--color-green)"
              columns={[
                {
                  title: "ID",
                  dataIndex: "id",
                  key: "id",
                },
                {
                  title: "Tên lệnh sản xuất",
                  dataIndex: "name",
                  key: "name",
                  render: (value: any, record: MrpProduction) => (
                    <a
                      href={`/mrp-productions/${record.id}`}
                      style={{
                        color: "#1976d2",
                        textDecoration: "underline",
                        cursor: "pointer",
                      }}
                      onClick={(e) => {
                        e.preventDefault();
                        router.push(`/mrp-productions/${record.id}`);
                      }}
                    >
                      {value}
                    </a>
                  ),
                },
                {
                  title: "Trạng thái",
                  dataIndex: "state",
                  key: "state",
                },
                {
                  title: "Sản phẩm",
                  dataIndex: "product_id",
                  key: "product_id",
                  render: (value: any) =>
                    value && Array.isArray(value) ? value[1] : value || "-",
                },
                {
                  title: "Số lượng",
                  dataIndex: "product_qty",
                  key: "product_qty",
                },
                {
                  title: "Ngày bắt đầu",
                  dataIndex: "date_start",
                  key: "date_start",
                },
                {
                  title: "Ngày kết thúc",
                  dataIndex: "date_finished",
                  key: "date_finished",
                },
                {
                  title: "Người phụ trách",
                  dataIndex: "user_id",
                  key: "user_id",
                  render: (value: any) =>
                    value && Array.isArray(value) ? value[1] : value || "-",
                },
                {
                  title: "Thao tác",
                  key: "action",
                  render: (_: any, record: MrpProduction) => (
                    <Tooltip title="Xóa">
                      <IconButton
                        onClick={() => handleDelete(record.id)}
                        sx={{ color: "var(--color-red)" }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  ),
                },
              ]}
            />
          </Paper>
        </Box>
      </Box>
    </Show>
  );
}
