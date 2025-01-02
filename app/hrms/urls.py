from django.urls import re_path
from . import views


urlpatterns = [
    re_path('hrms/createtask/', views.taskcreate, name='task_create'),
]
