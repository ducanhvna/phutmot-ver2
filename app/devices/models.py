from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Device(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255)
    os_version = models.CharField(max_length=255)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="devices", null=True, blank=True
    )

    # Các trường mới
    created_time = models.DateTimeField(auto_now_add=True)  # Lấy thời gian tạo tự động
    modified_time = models.DateTimeField(auto_now=True)  # Lấy thời gian sửa tự động

    def __str__(self):
        return f'{self.device_name}-{self.device_id}-{self.os_version}'
