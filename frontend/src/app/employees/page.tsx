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
import DateRangeIcon from "@mui/icons-material/DateRange";
import SharedTable from "@components/shared-table";
import {
  getAllEmployees,
  Employee,
} from "@/providers/employee-provider/employee-provider";

export default function Employees() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const router = useRouter();

  useEffect(() => {
    async function fetchEmployees() {
      const data = await getAllEmployees();
      setEmployees(data);
    }
    fetchEmployees();
  }, []);

  const handleDelete = (id: number) => {
    console.log(`Delete employee with ID: ${id}`);
    // Implement delete functionality
  };

  const handleNewRegistration = () => {
    router.push("/learning-data-entry/create");
  };

  return (
    <Show
      goBack={false}
      title={
        <Typography variant="h5" fontWeight="700">
          従業員一覧
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
              新規従業員登録
            </Button>
          </Box>

          <Paper
            elevation={2}
            sx={{ borderRadius: "10px", overflow: "hidden", mb: 3 }}
          >
            <SharedTable
              dataSource={employees}
              themeColor="var(--color-green)"
              columns={[
                {
                  title: "ID",
                  dataIndex: "id",
                  key: "id",
                },
                {
                  title: "氏名",
                  dataIndex: "name",
                  key: "name",
                },
                {
                  title: "メール",
                  dataIndex: "work_email",
                  key: "work_email",
                },
                {
                  title: "電話番号",
                  dataIndex: "work_phone",
                  key: "work_phone",
                },
                {
                  title: "職位",
                  dataIndex: "job_title",
                  key: "job_title",
                },
                {
                  title: "部署ID",
                  dataIndex: "department_id",
                  key: "department_id",
                },
                {
                  title: "ユーザーID",
                  dataIndex: "user_id",
                  key: "user_id",
                },
                {
                  title: "操作",
                  key: "action",
                  render: (_: any, record: Employee) => (
                    <Tooltip title="削除">
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
