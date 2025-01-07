from django.db import models


class Hrms(models.Model):
    company_code = models.CharField(max_length=50)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    info = models.JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company_code", "start_date", "end_date"],
                name="unique_dashboard_hrms",
            )
        ]

    def __str__(self):
        return self.company_name


class Fleet(models.Model):
    company_code = models.CharField(max_length=50)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    info = models.JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company_code", "start_date", "end_date"],
                name="unique_dashboard_fleet",
            )
        ]

    def __str__(self):
        return self.company_name


class Agriculture(models.Model):
    company_code = models.CharField(max_length=50)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField("Ngày bắt đầu tháng")
    end_date = models.DateField("Ngày kết thúc tháng")
    info = models.JSONField(default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company_code", "start_date", "end_date"],
                name="unique_dashboard_agri",
            )
        ]

    def __str__(self):
        return self.company_name
