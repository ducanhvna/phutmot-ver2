from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('db', 'url', 'username', 'password', 'company_name', 'company_code')
    search_fields = ('company_code', 'company_code')
