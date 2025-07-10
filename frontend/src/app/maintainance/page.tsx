'use client';
import React, { useEffect, useState } from 'react';
import { getAllEquipments, Equipment } from '@/providers/maintainance-provider/maintainance-provider';
import { Box, Typography, Paper, Divider, Stack } from '@mui/material';

const MaintainancePage: React.FC = () => {
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAllEquipments()
      .then(data => setEquipments(data))
      .catch(() => setError('Lỗi tải danh sách thiết bị'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Typography>Đang tải danh sách thiết bị...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" mb={3}>Danh sách thiết bị</Typography>
      <Paper elevation={2} sx={{ p: 2, borderRadius: '10px', bgcolor: 'var(--color-white)' }}>
        <Stack spacing={2}>
          {equipments.length === 0 ? (
            <Typography>Không có thiết bị nào.</Typography>
          ) : equipments.map(eq => (
            <Box key={eq.id}>
              <Typography variant="h6">{eq.name}</Typography>
              <Typography>ID: {eq.id}</Typography>
              <Typography>Số serial: {eq.serial_no || '-'}</Typography>
              <Typography>Phòng ban: {eq.department_id ? (Array.isArray(eq.department_id) ? eq.department_id[1] : eq.department_id) : '-'}</Typography>
              <Typography>Nhân viên được giao: {eq.employee_id ? (Array.isArray(eq.employee_id) ? eq.employee_id[1] : eq.employee_id) : '-'}</Typography>
              <Divider sx={{ my: 1 }} />
            </Box>
          ))}
        </Stack>
      </Paper>
    </Box>
  );
};

export default MaintainancePage;