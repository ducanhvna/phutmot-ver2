from django.contrib import admin
from .models import Scheduling, Leave


@admin.register(Scheduling)
class SchedulingAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')
