from django.db import models
from django.db.models import JSONField


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
    created_user = models.CharField("Người tạo", max_length=255)
    modified_user = models.CharField("Người sửa đổi", max_length=255)

    def __str__(self):
        return self.company_name
