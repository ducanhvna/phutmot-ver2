# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db import models
from django.conf import settings
from django.db.models.aggregates import Count
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
import string
# Create your models here.
def create_new_ref_number():
    code = get_random_string(8, allowed_chars=string.ascii_uppercase + string.digits)
    return code

class Company(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=512)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    dbname = models.CharField(max_length=200)
    api_version = models.CharField(max_length=200, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)

    # users = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     related_name='groups',
    #     through='Participation'
    # )
    def __str__(self):
        return self.name

class Device(models.Model):
    ANDROID = 1
    IPHONE = 2
    CHROME = 3
    MAC = 4
    WINDOW = 5
    OTHER = 6
    # referral = models.ForeignKey('Device',null=True,blank=True,on_delete=models.SET_NULL, related_name='childs')
    DEVICE_CHOICES = ((ANDROID, 'Android'), (IPHONE, 'iPhone') , (CHROME,'Chrome'), (MAC, 'MAC') , 
                      (WINDOW,'Window'), (OTHER,'Others'))
    type = models.SmallIntegerField(choices = DEVICE_CHOICES, default=OTHER)
    user   = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                    on_delete=models.CASCADE,
                                    primary_key=True, related_name='user_device')
    user_owner= models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='device_others')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    id = models.TextField(unique=True)
   
    default_shipping_address_id = models.IntegerField(null=True, blank=True)

    name   = models.CharField(max_length=8,
                null=False, blank=False, 
                unique=True,
                default=create_new_ref_number)
    device_firebase_address = models.CharField(max_length=255,
                null=True, 
                unique=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.user}"
   
class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title