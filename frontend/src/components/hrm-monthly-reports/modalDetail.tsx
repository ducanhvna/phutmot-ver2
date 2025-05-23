import React, { useState } from "react";
import { Typography, Input, Button, Checkbox, Select, DatePicker, message, Upload } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import dayjs, { Dayjs } from "dayjs";

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// Danh sách các lý do giải trình
const TAG_OPTIONS = ["Đi muộn", "Về sớm", "Ra ngoài", "Tăng ca", "Nghỉ phép", "Nghỉ lễ"];
const TIME_OPTIONS = [
  { label: "1 tiếng", value: 60 },
  { label: "3 tiếng", value: 180 },
  { label: "5 tiếng", value: 300 },
  { label: "Tùy chọn", value: "custom" },
];
const REASON_TYPE_OPTIONS = [
  { label: "Cá nhân", value: "personal" },
  { label: "Công việc", value: "work" },
];

const ModalDetail: React.FC<{ eventDetail: any }> = ({ eventDetail }) => {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [timeOption, setTimeOption] = useState<number | "custom">(60);
  const [customTime, setCustomTime] = useState<number>(0);
  const [startTime, setStartTime] = useState<Dayjs | null>(null);
  const [endTime, setEndTime] = useState<Dayjs | null>(null);
  const [reason, setReason] = useState<string>("");
  const [reasonType, setReasonType] = useState<string>("personal");
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);

  // Xử lý chọn lý do giải trình
  const handleTagChange = (tag: string, checked: boolean) => {
    setSelectedTags(checked ? [...selectedTags, tag] : selectedTags.filter(t => t !== tag));
  };

  // Xử lý gửi dữ liệu
  const handleUpload = () => {
    if (!reason.trim()) {
      message.error("Vui lòng nhập lý do giải trình!");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      const isOk = Math.random() > 0.2;
      if (isOk) {
        message.success("Upload thành công!");
      } else {
        message.error("Upload thất bại!");
      }
    }, 1000);
  };

  // Helper: tính trạng thái hoàn thành (is_complete) cho AttendanceRecord
  function isAttendanceComplete(record: any): boolean {
    return record.total_work_time < record.actual_total_work_time;
  }

  return (
    <>
      <Title level={5}>Ca làm việc</Title>
      <p>{eventDetail?.shift || "Không có ca làm việc"}</p>

      <Title level={5}>Số phút làm việc</Title>
      <p>{eventDetail?.total_work_time || 0} phút</p>

      <Title level={5}>Trạng thái</Title>
      <p>{isAttendanceComplete(eventDetail) ? "Hoàn thành" : "Chưa hoàn thành"}</p>

      <Title level={4}>Giải trình lý do</Title>

      {/* Upload danh sách file đính kèm */}
      <Title level={5}>File đính kèm</Title>
      <Upload 
        multiple
        fileList={fileList}
        onChange={({ fileList }) => setFileList(fileList)}
        beforeUpload={() => false}
      >
        <Button icon={<UploadOutlined />}>Upload file</Button>
      </Upload>

      {/* Lý do giải trình - GIỮ NGUYÊN TAG_OPTIONS */}
      <Title level={5}>Chọn lý do</Title>
      {TAG_OPTIONS.map((tag) => (
        <Checkbox key={tag} checked={selectedTags.includes(tag)} onChange={(e) => handleTagChange(tag, e.target.checked)}>
          {tag}
        </Checkbox>
      ))}

      {/* Lựa chọn thời gian giải trình */}
      <Title level={5}>Thời gian giải trình</Title>
      <Select value={timeOption} onChange={setTimeOption} style={{ width: 150 }}>
        {TIME_OPTIONS.map((option) => (
          <Option key={option.value} value={option.value}>
            {option.label}
          </Option>
        ))}
      </Select>

      {timeOption === "custom" && (
        <Input type="number" placeholder="Nhập số phút" value={customTime} onChange={(e) => setCustomTime(Number(e.target.value))} />
      )}

      {/* Thời gian bắt đầu & kết thúc */}
      <Title level={5}>Khoảng thời gian</Title>
      <DatePicker showTime value={startTime} onChange={(date) => setStartTime(date)} placeholder="Thời gian bắt đầu" />
      <DatePicker showTime value={endTime} onChange={(date) => setEndTime(date)} placeholder="Thời gian kết thúc" />

      {/* Lựa chọn loại lý do */}
      <Title level={5}>Loại lý do</Title>
      <Select value={reasonType} onChange={setReasonType} style={{ width: 150 }}>
        {REASON_TYPE_OPTIONS.map((option) => (
          <Option key={option.value} value={option.value}>
            {option.label}
          </Option>
        ))}
      </Select>

      {/* Nhập chi tiết lý do */}
      <Title level={5}>Mô tả chi tiết</Title>
      <TextArea rows={4} value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Nhập lý do..." />

      {/* Nút gửi */}
      <Button type="primary" onClick={handleUpload} loading={loading} style={{ marginTop: 10 }}>
        Gửi giải trình
      </Button>
    </>
  );
};

export default ModalDetail;
