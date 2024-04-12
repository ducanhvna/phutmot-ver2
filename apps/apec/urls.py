from django.urls import path, include , re_path
from apps.home import views
from .views import SyncUserDevice, GetListCompany, GetListHrmEmployees, \
                        GetListHrmAttendanceReport

urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='apec_syncuser'),
    path("listcompany/", GetListCompany.as_view(), name='v2_list'),
    path("hrmemployees/", GetListHrmEmployees.as_view(), name='v2_list_employee'),
    path("hrmattendances/", GetListHrmAttendanceReport.as_view(), name='v2_list_attendance'),
]
