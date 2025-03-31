from django.contrib import admin
from .models import Device


@admin.register(Device)
class FleetAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'device_name', 'os_version', 'user')
    search_fields = ('device_id', 'device_name', 'os_version', 'user')
