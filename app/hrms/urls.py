from django.urls import path
from .views import TaskCreateView


urlpatterns = [
    path('create-task/', TaskCreateView.as_view(), name='task-create'),
]
