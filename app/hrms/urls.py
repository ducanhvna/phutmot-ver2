from django.urls import re_path
from . import views


urlpatterns = [
    re_path('createtask/', views.taskcreate, name='task_create2'),
]
