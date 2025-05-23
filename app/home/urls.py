from django.urls import path, re_path, include
from .views import LoginView, handle_telegram_user, EmployeeWithSchedulingListAPIView
from . import views
# from hrms.views import taskcreate


urlpatterns = [
    path('', views.index, name='index'),
    re_path('timesheet/', views.timesheet, name='timesheet'),
    re_path('personal/', views.personal_timesheet, name='personal_timesheet'),
    path('hrms/', include('hrms.urls')),
    path('documents', include('documents.urls')),
    path('api/telegram-user/', handle_telegram_user, name='handle_telegram_user'),
    path('api/chat/', include('bot_manager.urls')),
    path('api/login/', LoginView.as_view(), name='login'),
    # re_path('createtask/', taskcreate, name='task_create2'),
    re_path('api/get_details', views.get_details, name='detail_timesheet'),
    path('api/employee/search/', views.UserProfileAPIView.as_view(), name='employee_search'),
    path('apiv2/', include('devices.urls')),
    path('api/hrms/employee_scheduling/', EmployeeWithSchedulingListAPIView.as_view(), name='employee_with_scheduling_list'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
