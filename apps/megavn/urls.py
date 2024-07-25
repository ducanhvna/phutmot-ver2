from django.urls import path, include , re_path
from .views import GetListEmployee, ErpProfile

urlpatterns = [
    path("employee/", GetListEmployee.as_view(), name='megavn_listemployee'),
    path("profile/", ErpProfile.as_view(), name='megavn_profile'),
]