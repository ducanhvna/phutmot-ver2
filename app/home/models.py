from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User


class Company(models.Model):
    db = models.CharField(max_length=255)
    url = models.URLField(max_length=200)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    company_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255)
    info = JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    def __str__(self):
        return self.company_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='profile', null=True, blank=True)
    employee_code = models.CharField("Mã nhân sự", max_length=255, null=True, blank=True)
    info = JSONField(default=dict)  # Thông tin profile dạng JSON
    other_profile = JSONField("Hồ sơ khác", default=list, blank=True)
    contracts = JSONField(default=list)  # Danh sách hợp đồng dạng JSON
    al = JSONField(default=list)  # Dữ liệu phép dạng JSON
    cl = JSONField(default=list)  # Dữ liệu bù dạng JSON
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee_code'],
                name='unique_employee_code',
                condition=models.Q(employee_code__isnull=False)
            )
        ]

    def __str__(self):
        return f"{self.user.username}'s profile" if self.user else "<anonymous>"
