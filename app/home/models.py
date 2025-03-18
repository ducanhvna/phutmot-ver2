from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User
from unidecode import unidecode


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
    info_unaccented = models.JSONField("Thông tin bổ sung không dấu", default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee_code'],
                name='unique_employee_code',
                condition=models.Q(employee_code__isnull=False)
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
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s profile" if self.user else "<anonymous>"


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='teleprofile', null=True, blank=True)
    telegram_id = models.CharField(max_length=255, unique=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.telegram_username} ({self.telegram_id})"


class OdooUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='odoouser', null=True, blank=True)
    login = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, unique=True)
    apikey = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.login}"
