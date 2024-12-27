from django.contrib import admin
from .models import Company, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('db', 'url', 'username', 'password', 'company_name', 'company_code')
    search_fields = ('company_code', 'company_code')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'create_time', 'update_time', 'user')
    search_fields = ('employee_code', 'user')
