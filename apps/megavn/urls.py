from django.urls import path, include , re_path
from .views import GetListEmployee

urlpatterns = [
    path("employee/", GetListEmployee.as_view(), name='megavn_listemployee'),
]