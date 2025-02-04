from django.db import models
from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    google_doc_link = models.URLField(blank=True, null=True)
    info = models.JSONField("Thông tin tài liệu", default=dict, blank=True)
    other_profile = models.JSONField("Thông tin khác", default=dict, blank=True)
    create_time = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    update_time = models.DateTimeField("Thời gian cập nhật", auto_now=True)

    def __str__(self):
        return self.title
