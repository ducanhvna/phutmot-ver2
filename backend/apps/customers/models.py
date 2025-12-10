from django.db import models
from django.utils import timezone
import unicodedata


def strip_accents(text):
    """
    Loại bỏ dấu tiếng Việt và chuyển về lowercase
    """
    if not text:
        return None
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text.lower()


class Customer(models.Model):
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    id_card_number = models.CharField(max_length=20, null=True)
    old_id_card_number = models.CharField(max_length=20, blank=True, null=True)
    other_id_card_number = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255, blank=True, null=True)
    verification_status = models.BooleanField(default=False)

    # Trường bổ sung
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        blank=True,
        null=True
    )
    birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Thông tin về store profile
    info = models.JSONField(blank=True, null=True, help_text='Thông tin về store profile')

    # Thời gian hoạt động mới nhất tại cửa hàng
    last_store_activity_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def touch_store_activity(self, at=None):
        """
        Cập nhật thời gian hoạt động mới nhất tại cửa hàng
        """
        self.last_store_activity_at = at or timezone.now()
        self.save(update_fields=["last_store_activity_at"])

    def save(self, *args, **kwargs):
        # Tự động sinh english_name từ name
        if self.name:
            self.english_name = strip_accents(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class IdentifierType(models.TextChoices):
    PHONE = "phone", "Phone"
    NATIONAL_ID = "national_id", "National ID"
    EMAIL = "email", "Email"
    USERNAME = "username", "Username"
    OTHER = "other", "Other"


class ActivityType(models.TextChoices):
    VISIT = "visit", "Visit"
    PURCHASE = "purchase", "Purchase"
    DEPOSIT = "deposit", "Deposit"
    INQUIRY = "inquiry", "Inquiry"
    LOGIN = "login", "Login"
    OTHER = "other", "Other"


class CustomerActivity(models.Model):
    # Định danh linh hoạt
    identifier_type = models.CharField(max_length=32, choices=IdentifierType.choices)
    identifier_value = models.CharField(max_length=255)
    identifier_normalized = models.CharField(max_length=255, db_index=True, blank=True)
    canonical_id = models.CharField(max_length=300, db_index=True)

    # Thông tin hoạt động
    activity_type = models.CharField(max_length=32, choices=ActivityType.choices, default=ActivityType.OTHER)
    channel = models.CharField(max_length=64, blank=True)     # vd: "store", "web", "app"
    store_code = models.CharField(max_length=64, blank=True)  # mã cửa hàng (nếu có)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    metadata = models.JSONField(default=dict, blank=True)
    note = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["identifier_type", "identifier_normalized"]),
            models.Index(fields=["canonical_id"]),
            models.Index(fields=["occurred_at"]),
        ]
        ordering = ["-occurred_at", "-created_at"]

    def save(self, *args, **kwargs):
        normalized = self._normalize_identifier(self.identifier_type, self.identifier_value)
        self.identifier_normalized = normalized or self.identifier_value
        self.canonical_id = f"{self.identifier_type}:{self.identifier_normalized}"
        super().save(*args, **kwargs)

    @staticmethod
    def _normalize_identifier(identifier_type: str, value: str) -> str:
        if value is None:
            return ""
        v = str(value).strip()
        if identifier_type == IdentifierType.EMAIL:
            return v.lower()
        if identifier_type == IdentifierType.USERNAME:
            return v.lower()
        if identifier_type == IdentifierType.PHONE:
            return v.replace(" ", "").replace("+", "")
        if identifier_type == IdentifierType.NATIONAL_ID:
            return v.replace(" ", "").upper()
        return v

    def __str__(self):
        return f"{self.canonical_id} - {self.activity_type} @ {self.occurred_at:%Y-%m-%d %H:%M}"
