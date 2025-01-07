from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_place', 'start_date', 'end_date', 'create_time', 'update_time')
    search_fields = ('license_place', 'start_date', 'end_date')
