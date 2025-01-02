from django.urls import path, re_path, include
from . import views
# from hrms.views import taskcreate


urlpatterns = [
    path('', views.index, name='index'),
    re_path('timesheet/', views.timesheet, name='timesheet'),
    path('hrms/', include('hrms.urls')),
    # re_path('createtask/', taskcreate, name='task_create2'),
    re_path('api/get_details', views.get_details, name='detail_timesheet'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
