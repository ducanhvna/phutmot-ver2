from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'company_code', 'name', 'company_name', 'start_date', 'end_date')
    search_fields = ('code', 'company_code', 'name', 'company_name', 'start_date', 'end_date')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date')
    search_fields = ('employee_code', 'start_date', 'end_date')
