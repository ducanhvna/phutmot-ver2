from django.urls import path, include , re_path
from .views import GetListEmployee, ErpProfile, ErpLink, getDeviceToken

urlpatterns = [
    path("employee/", GetListEmployee.as_view(), name='megavn_listemployee'),
    path("profile/", ErpProfile.as_view(), name='megavn_profile'),
    
    path("linkerp/", ErpLink.as_view(), name='megavn_linkerp'),
    path("getdevicetoken/", getDeviceToken.as_view(), name='megavn_device_token'),
]