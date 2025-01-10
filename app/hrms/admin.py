from django.contrib import admin
from .models import Scheduling, Leave, Attendance, Employee, Shifts, Explaination, Timesheet


@admin.register(Shifts)
class ShiftsAdmin(admin.ModelAdmin):
    list_display = ('company_code', 'name', 'start_work_time', 'end_work_time', 'start_rest_time', 'end_rest_time')
    search_fields = ('company_code', 'name', 'start_work_time', 'end_work_time', 'start_rest_time')


@admin.register(Scheduling)
class SchedulingAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('code', 'start_date', 'end_date')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')


@admin.register(Explaination)
class ExplainationAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('employee_code', 'start_date', 'end_date')
