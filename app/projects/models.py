from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User
from unidecode import unidecode


class Project(models.Model):
    employee_code = models.CharField(max_length=255)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    info = JSONField(default=dict, blank=True)
    info_unaccented = models.JSONField("Thông tin bổ sung không dấu", default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee_code", "start_date", "end_date"],
                name="unique_code_project_company",
            )
        ]

    def save(self, *args, **kwargs):
        if self.info:
            self.info_unaccented = {}
            for key, value in self.info.items():
                if isinstance(value, str):
                    self.info_unaccented[key] = unidecode(value).lower()
                else:
                    self.info_unaccented[key] = value  # Giữ nguyên giá trị cho các kiểu dữ liệu khác
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return f"({self.company_code}.{self.code}) - {self.name} info from {self.start_date} to {self.end_date}"


class Task(models.Model):
    employee_code = models.CharField("Mã nhân sự", max_length=255, null=True, blank=True)
    progress_records = JSONField("Trạng thái các nhiệm vụ theo ngày", default=list, blank=True)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee_code", "start_date", "end_date"],
                name="unique_employee_task_project",
            )
        ]

    def __str__(self):
        return f"Task Progress {self.employee_code} from {self.start_date} to {self.end_date}"
