from django.db import models
from datetime import datetime, date, timedelta
from django.db.models import JSONField


class Employee(models.Model):
    employee_code = models.CharField("Mã nhân sự", max_length=255, unique=True)
    info = JSONField("Thông tin bổ sung", default=dict, blank=True)
    other_profile = JSONField("Hồ sơ khác", default=list, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)
    # created_user = models.CharField("Người tạo", max_length=255)
    # modified_user = models.CharField("Người sửa đổi", max_length=255)

    def __str__(self):
        return self.employee_code


class Attendance(models.Model):
    employee_code = models.CharField("Mã nhân sự", max_length=255, unique=True)
    attendance_records = JSONField("Thông tin điểm danh", default=list, blank=True)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)
    # created_user = models.CharField("Người tạo", max_length=255)
    # modified_user = models.CharField("Người sửa đổi", max_length=255)

    def __str__(self):
        return f"Attendance for {self.employee_code} from {self.start_date} to {self.end_date}"

    def add_attendance_record(self, record):
        """
        Thêm một dòng vào mảng JSON `attendance_records`.
        """
        self.attendance_records.append(record)
        self.save()


class Shifts(models.Model):
    name = models.CharField("Mã ca", max_length=255, unique=False)
    start_work_time = models.TimeField("Giờ bắt đầu làm:", null=False, blank=False)
    end_work_time = models.TimeField("Giờ kết thúc làm:", null=False, blank=False)
    start_rest_time = models.TimeField("Giờ bắt đầu nghỉ:", null=True, blank=True)
    end_rest_time = models.TimeField("Giờ kết thúc nghỉ:", null=True, blank=True)
    total_work_time = models.FloatField("Tổng thời gian làm việc", null=True, blank=True)  # Compute field
    total_rest_time = models.FloatField("Tổng thời gian nghỉ", null=True, blank=True)  # Compute field
    company_code = models.CharField("Mã công ty", max_length=255, null=True, blank=True)  # Thay thế cho company_id
    breakfast = models.BooleanField("Ăn sáng", default=False)
    lunch = models.BooleanField("Ăn trưa", default=False)
    dinner = models.BooleanField("Ăn tối", default=False)
    night = models.BooleanField("Đêm", default=False)
    fix_rest_time = models.BooleanField("Ca gãy", default=False)
    rest_shifts = models.BooleanField("Ca nghỉ", default=False)
    number_of_attendance = models.IntegerField('Số lần chấm công', null=True, blank=True)
    day_work_value = models.FloatField("Giá trị ngày làm việc", null=True, blank=True)
    free_time = models.FloatField("Thời gian tự do", null=True, blank=True, default=0)
    info = JSONField("Thông tin bổ sung", default=dict, blank=True)  # Thêm trường JSON cho thông tin bổ sung

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Thêm logic để tính toán các trường compute
        self.total_work_time = self._compute_total_work_time()
        self.total_rest_time = self._compute_total_rest_time()
        super(Shifts, self).save(*args, **kwargs)

    def _compute_total_work_time(self):
        # Tính toán tổng thời gian làm việc
        start = datetime.combine(date.min, self.start_work_time)
        end = datetime.combine(date.min, self.end_work_time)
        if end <= start:
            end += timedelta(days=1)  # Xử lý trường hợp ca làm việc kéo dài qua đêm
        delta = end - start
        return delta.total_seconds() / 3600  # Chuyển đổi thành giờ

    def _compute_total_rest_time(self):
        # Tính toán tổng thời gian nghỉ
        if self.start_rest_time and self.end_rest_time:
            start = datetime.combine(date.min, self.start_rest_time)
            end = datetime.combine(date.min, self.end_rest_time)
            if end <= start:
                end += timedelta(days=1)  # Xử lý trường hợp ca nghỉ kéo dài qua đêm
            delta = end - start
            return delta.total_seconds() / 3600  # Chuyển đổi thành giờ
        return 0


class Scheduling(models.Model):
    employee_code = models.CharField("Mã nhân sự", max_length=255, unique=True)
    scheduling_records = JSONField("Thông tin chấm công", default=list, blank=True)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)
    # created_user = models.CharField("Người tạo", max_length=255)
    # modified_user = models.CharField("Người sửa đổi", max_length=255)

    def __str__(self):
        return f"Scheduling {self.employee_code} from {self.start_date} to {self.end_date}"


class Leave(models.Model):
    employee_code = models.CharField("Mã nhân sự", max_length=255, unique=True)
    leave_records = JSONField("Danh sách đơn", default=list, blank=True)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)
    # created_user = models.CharField("Người tạo", max_length=255)
    # modified_user = models.CharField("Người sửa đổi", max_length=255)

    def __str__(self):
        return f"Hr leave {self.employee_code} from {self.start_date} to {self.end_date}"