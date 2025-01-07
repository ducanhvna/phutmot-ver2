from django.contrib import admin
from .models import Fleet, Hrms


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ('company_code', 'company_name', 'start_date', 'end_date')
    search_fields = ('company_code', 'company_name', 'start_date', 'end_date')


@admin.register(Hrms)
class HrmsAdmin(admin.ModelAdmin):
    list_display = ('company_code', 'company_name', 'start_date', 'end_date')
    search_fields = ('company_code', 'company_name', 'start_date', 'end_date')
