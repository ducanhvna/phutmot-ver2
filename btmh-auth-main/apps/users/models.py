from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email=None, username=None, password=None, **extra_fields):
        if not email and not username:
            raise ValueError("Email hoặc Username là bắt buộc")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email=email, username=username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    # Trường JSON lưu thông tin thêm
    info = models.JSONField(default=dict, blank=True)

    # Trường 4 ký tự đại diện (ví dụ dùng cho Odoo sync)
    code4 = models.CharField(max_length=4, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"   # mặc định login bằng username
    REQUIRED_FIELDS = ["email"]   # khi tạo superuser yêu cầu email

    objects = UserManager()

    def __str__(self):
        return self.username or self.email
