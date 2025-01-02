from django.urls import re_path
from . import views


urlpatterns = [
    re_path('task/create', views.taskcreate, name='task_create2'),
]
