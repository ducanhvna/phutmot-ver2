"use client";
import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./styles.module.css";
import ScheduleTable from "@/components/hrm-monthly-reports/scheduleTable";
import { fetchEmployees, Employee } from "@/providers/data-provider/employee-provider";
import { getAccessTokenFromCookie } from "@/providers/auth-provider/auth-provider.client";

const MonthlyReportPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [employees, setEmployees] = useState<Employee[]>([]);

  useEffect(() => {
    let token = getAccessTokenFromCookie();
    if (!token) {
      token = "dumy_token"; // Dummy token for testing
    }
    if (!token) return;
    const month = selectedDate.getMonth() + 1;
    const year = selectedDate.getFullYear();
    fetchEmployees(token, month, year).then(setEmployees);
  }, [selectedDate]);

  return (
    <div>
      <label>Chọn tháng/năm: </label>
      <div className={styles.datePickerWrapper}>
        <DatePicker
          selected={selectedDate}
          onChange={(date: Date | null) => setSelectedDate(date || new Date())}
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
      />
    </div>
  );
};

export default MonthlyReportPage;
