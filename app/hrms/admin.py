from django.contrib import admin
from .models import Scheduling


@admin.register(Scheduling)
class SchedulingAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'scheduling_records')
    search_fields = ('employee_code', 'start_date', 'end_date')
