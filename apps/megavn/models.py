from django.db import models

class MegaEmployee(models.Model):
    code = models.CharField(max_length=20,null=False, blank=False, unique=True)
    group = models.CharField(max_length=50,null=True, blank=True)
    name = models.CharField(max_length=200,null=False, blank=False)
    department = models.CharField(max_length=50,null=True, blank=True)
    other = models.CharField(max_length=50,null=True, blank=True)
    title = models.CharField(max_length=50,null=True, blank=True)
    email = models.CharField(max_length=100,null=True, blank=True)
    chat_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.code} - {self.name}'
