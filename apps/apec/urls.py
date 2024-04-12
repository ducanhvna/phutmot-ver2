from django.urls import path, include , re_path
from apps.home import views
from .views import SyncUserDevice

urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='apec_syncuser'),
]
