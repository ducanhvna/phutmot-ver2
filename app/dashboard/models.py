from django.db import models


class Hrms(models.Model):
    company_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255)
    info = models.JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    def __str__(self):
        return self.company_name


class Fleet(models.Model):
    company_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255)
    info = models.JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    def __str__(self):
        return self.company_name
