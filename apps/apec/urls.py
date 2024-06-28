from django.urls import path, include , re_path
from .views import SyncUserDevice, GetListCompany, GetListHrmEmployees, \
                        GetListHrmAttendanceReport, GetListTask, FeedFetch, fetchRoomByMonth, fetchChatAttendance

urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='apec_syncuser'),
    path("listcompany/", GetListCompany.as_view(), name='v2_list'),
    path("hrmemployees/", GetListHrmEmployees.as_view(), name='v2_list_employee'),
    path("hrmattendances/", GetListHrmAttendanceReport.as_view(), name='v2_list_attendance'),
    path("owntasks/", GetListTask.as_view(), name='v2_owntasks'),
    path("feedfetch/", FeedFetch.as_view(), name='v2_feedfetch'),
    path("fetchcomments/", GetListTask.as_view(), name='v2_fetchcomments'),
    path("fetchroomsbymonth/", fetchRoomByMonth.as_view(), name='v2_fetchrooms'),
    path("<int:attendanceId>/fetchchat/", fetchChatAttendance.as_view(), name='v2_fetchchat'),
]
