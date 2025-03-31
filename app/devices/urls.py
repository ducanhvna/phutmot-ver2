from django.urls import path
from .views import device_login


app_name = "devices"


urlpatterns = [
    path('device-login/', device_login, name='device_login')
]
