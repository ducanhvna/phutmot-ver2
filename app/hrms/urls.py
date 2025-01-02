from django.urls import path
from . import views


urlpatterns = [
    path('create-task/', views.taskcreate, name='task-create'),
]
