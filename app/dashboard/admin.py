from django.contrib import admin
from .models import Fleet


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ('company_code', 'company_name', 'start_date', 'end_date')
    search_fields = ('company_code', 'company_name', 'start_date', 'end_date')
