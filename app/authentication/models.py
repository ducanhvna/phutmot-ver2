# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present hinosoft.com
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)  # Trường để lưu mã nhân viên
    employee_info = JSONField(default=dict)  # Trường JSONField để lưu thông tin bổ sung
    other_employees_info = JSONField(default=list)  # Trường JSONField để lưu thông tin nhân viên khi chuyển công ty

    def __str__(self):
        return self.user.username
