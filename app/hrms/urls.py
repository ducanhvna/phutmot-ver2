from django.urls import path
from .views import (
    TaskCreateView,
    TaskCreateAPIView,
    AlTablesView,
    ClTablesView,
    Employees,
)

app_name = 'hrms'


urlpatterns = [
    path('core/employees', Employees.as_view(), name='core_employees'),
    path('al/tables', AlTablesView.as_view(), name='al_tables'),
    path('cl/tables', ClTablesView.as_view(), name='cl_tables'),
    path('task/create', TaskCreateView.as_view(), name='create_task'),
    path('api/create_task/', TaskCreateAPIView.as_view(), name='api_create_task'),
]
