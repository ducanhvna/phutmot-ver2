from django.urls import path
from django.contrib.auth.models import User
from .views import SyncUserDevice, GetListCompany, GetListHrmEmployees
urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='vantai_api_syncuser'),
    path("listcompany/", GetListCompany.as_view(), name='vantai_api_listcompany'),
    path("hrmemployees/", GetListHrmEmployees.as_view(), name='vantai_api_list_employee'),
]