from django.db import models
from datetime import datetime, date, timedelta
from django.db.models import JSONField


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
