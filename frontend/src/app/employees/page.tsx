'use client';
import React, { useEffect, useState } from 'react';
import { getAllEmployees, Employee } from '@/providers/employee-provider/employee-provider';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAllEmployees()
      .then(data => {
        // Lọc bỏ các phần tử không phải object hoặc có function (phòng lỗi serialize)
        const filtered = Array.isArray(data)
          ? data.filter(emp => emp && typeof emp === 'object' && !Object.values(emp).some(v => typeof v === 'function'))
          : [];
        setEmployees(filtered);
      })
      .catch(err => setError('Lỗi tải danh sách nhân viên'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Đang tải danh sách nhân viên...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Danh sách nhân viên</h1>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên</th>
            <th>Email</th>
            <th>Điện thoại</th>
            <th>Chức vụ</th>
            <th>Phòng ban</th>
          </tr>
        </thead>
        <tbody>
          {employees.map(emp => (
            <tr key={emp.id}>
              <td>{emp.id}</td>
              <td>{emp.name}</td>
              <td>{emp.work_email || '-'}</td>
              <td>{emp.work_phone || '-'}</td>
              <td>{emp.job_title || '-'}</td>
              <td>{emp.department_id ? (Array.isArray(emp.department_id) ? emp.department_id[1] : emp.department_id) : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}