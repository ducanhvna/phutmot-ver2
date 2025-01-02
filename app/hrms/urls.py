from django.urls import path
from .views import TaskCreateView, TaskCreateAPIView

app_name = 'hrms'


urlpatterns = [
    path('task/create', TaskCreateView.as_view(), name='create_task'),
    path('api/create_task/', TaskCreateAPIView.as_view(), name='api_create_task'),
]
