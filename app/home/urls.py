from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    re_path('timesheet/', views.timesheet, name='timesheet'),
    re_path('api/get_details', views.get_details, name='detail_timesheet'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
