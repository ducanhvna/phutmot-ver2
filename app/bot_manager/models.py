from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    telegram_user_id = models.CharField(max_length=100, unique=True)

class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
