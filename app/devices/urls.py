from django.urls import path
from .views import DeviceLoginView


app_name = "devices"


urlpatterns = [
    path('device-login/', DeviceLoginView.as_view(), name='device_login')
]
