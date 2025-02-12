from django.urls import path
from .views import TaskCreateView, TaskCreateAPIView, AlTablesView, ClTablesView

app_name = 'hrms'


urlpatterns = [
    path('al/tables', AlTablesView.as_view(), name='al_tables'),
    path('cl/tables', ClTablesView.as_view(), name='cl_tables'),
    path('task/create', TaskCreateView.as_view(), name='create_task'),
    path('api/create_task/', TaskCreateAPIView.as_view(), name='api_create_task'),
]
