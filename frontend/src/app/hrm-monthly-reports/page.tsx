"use client";
import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styles from "./styles.module.css";
import ScheduleTable from "@/components/hrm-monthly-reports/scheduleTable";

const MonthlyReportPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  return (
    <div>
      <label>Chọn tháng/năm: </label>
      <div className={styles.datePickerWrapper}>
        <DatePicker
          selected={selectedDate}
          onChange={(date) => setSelectedDate(date || new Date())}
          dateFormat="MM/yyyy"
          showMonthYearPicker
          showFullMonthYearPicker
          showFourColumnMonthYearPicker
          placeholderText="Chọn tháng/năm"
          className={styles.datePicker} // ✅ Áp dụng style mới
        />
      </div>

      {/* Truyền tháng và năm từ DatePicker vào ScheduleTable */}
      <ScheduleTable month={selectedDate.getMonth() + 1} year={selectedDate.getFullYear()} />
    </div>
  );
};

export default MonthlyReportPage;
