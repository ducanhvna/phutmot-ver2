"use client";
import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./styles.module.css";
import ScheduleTable from "@/components/hrm-monthly-reports/scheduleTable";
import { fetchEmployeesWithScheduling, Employee } from "@/providers/data-provider/employee-provider";
import { getAccessTokenFromCookie } from "@/providers/auth-provider/auth-provider.client";

const MonthlyReportPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20; // hoặc giá trị mặc định bạn muốn

  // Tính month và year từ selectedDate
  const month = selectedDate.getMonth() + 1;
  const year = selectedDate.getFullYear();

  useEffect(() => {
    let token = getAccessTokenFromCookie();
    if (!token) {
      token = "dumy_token"; // Dummy token for testing
    }
    if (!token) return;
    fetchEmployeesWithScheduling(token, currentPage, pageSize, month, year).then((data) => {
      setEmployees(data.results);
      setTotal(data.count);
    });
  }, [selectedDate, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div>
      <label>Chọn tháng/năm: </label>
      <div className={styles.datePickerWrapper}>
        <DatePicker
          selected={selectedDate}
          onChange={(date: Date | null) => {
            setSelectedDate(date || new Date());
            setCurrentPage(1); // reset về trang 1 khi đổi tháng
          }}
          dateFormat="MM/yyyy"
          showMonthYearPicker
          showFullMonthYearPicker
          showFourColumnMonthYearPicker
          placeholderText="Chọn tháng/năm"
          className={styles.datePicker}
        />
      </div>
      <ScheduleTable
        employees={employees}
        month={selectedDate.getMonth() + 1}
        year={selectedDate.getFullYear()}
        total={total}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
      />
    </div>
  );
};

export default MonthlyReportPage;
