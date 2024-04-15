from django.urls import path
from django.contrib.auth.models import User
from .views import SyncUserDevice
urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='apec_syncuser'),
]