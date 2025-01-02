from django.urls import re_path
from .views import TaskCreateView


urlpatterns = [
    re_path('task/create', TaskCreateView.as_view(), name='task_create'),
]
