from django.urls import path, re_path, include
from .views import LoginView
from . import views
# from hrms.views import taskcreate


urlpatterns = [
    path('', views.index, name='index'),
    re_path('timesheet/', views.timesheet, name='timesheet'),
    path('hrms/', include('hrms.urls')),
    path('documents', include('documents.urls')),
    path('api/chat/', include('bot_manager.urls')),
    path('api/login/', LoginView.as_view(), name='login'),
    # re_path('createtask/', taskcreate, name='task_create2'),
    re_path('api/get_details', views.get_details, name='detail_timesheet'),
    path('api/employee/search/', views.UserProfileAPIView.as_view(), name='employee_search'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
