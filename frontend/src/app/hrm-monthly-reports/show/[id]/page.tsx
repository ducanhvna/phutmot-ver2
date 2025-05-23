"use client";
import { useRouter } from "next/navigation";
import { Modal, Spin } from "antd";
import React, { useState, useEffect } from "react";
import { fetchDetail, AttendanceRecord } from "@/providers/data-provider/employee-provider";
import ModalDetail from "@/components/hrm-monthly-reports/modalDetail";

// type AttendanceRecord = {
//   id: number;
//   name: string;
//   date: string;
//   status: string;
// };

export default function HrmMonthlyReportShow({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [eventDetail, setEventDetail] = useState<AttendanceRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(true);

  useEffect(() => {
    const rawId = params.id;
    if (!rawId) {
      console.error("Attendance ID bị null hoặc undefined!");
      setIsLoading(false);
      return;
    }

    const attendanceId = Number(rawId);
    if (isNaN(attendanceId) || attendanceId <= 0 || !Number.isInteger(attendanceId)) {
      console.error(`Lỗi: params.id không phải là số hợp lệ (${params.id})`);
      setIsLoading(false);
      return;
    }

    // Lấy token từ cookie sau khi login
    const getTokenFromCookie = () => {
      if (typeof document === "undefined") return "";
      const match = document.cookie.match(/(?:^|; )access_token=([^;]*)/);
      return match ? decodeURIComponent(match[1]) : "";
    };
    const token = getTokenFromCookie();
    if (!token) {
      console.error("Không tìm thấy access_token trong cookie!");
      setIsLoading(false);
      return;
    }

    // Gọi API nếu attendanceId hợp lệ và có token
    fetchDetail(attendanceId, token).then((data) => {
      if (!data) {
        console.warn(`Không tìm thấy dữ liệu cho Attendance ID: ${attendanceId}`);
        setIsLoading(false);
        return;
      }
      setEventDetail(data as AttendanceRecord);
      setIsLoading(false);
    });
  }, [params.id]);

  return (
    <Modal
      title={`Chi tiết điểm danh ${params.id}`}
      open={isModalOpen}
      onCancel={() => router.push("/hrm-monthly-reports")}
      footer={null}
    >
      {isLoading ? (
        <Spin size="large" />
      ) : eventDetail ? (
        <ModalDetail eventDetail={eventDetail} />
      ) : (
        <p style={{ color: "red" }}>Không tìm thấy dữ liệu cho ID: {params.id}</p>
      )}
    </Modal>
  );
}
