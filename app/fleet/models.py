from django.db import models


class Vehicle(models.Model):
    license_place = models.CharField("Biển số xe", max_length=255)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    info = models.JSONField("Thông tin xe", default=dict, blank=True)
    other_profile = models.JSONField("Thông tin khác", default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["license_place", "start_date", "end_date"],
                name="unique_fleet_Vehicle",
            )
        ]

    def __str__(self):
        return self.license_place
