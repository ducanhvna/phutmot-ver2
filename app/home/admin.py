from django.contrib import admin
from .models import Company, UserProfile
from django.utils.html import format_html
import json


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('db', 'url', 'username', 'password', 'company_name', 'company_code')
    search_fields = ('company_name', 'company_code')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'display_contracts', 'create_time', 'update_time', 'user')
    search_fields = ('employee_code', 'user')

    def display_contracts(self, obj):
        try:
            contracts = obj.contracts
            html = '<table>'
            for contract in contracts:
                html += '<tr>'
                for key, value in contract.items():
                    html += f'<th>{key}</th><td>{value}</td>'
                html += '</tr>'
            html += '</table>'
            return format_html(html)
        except json.JSONDecodeError:
            return "Invalid JSON"

    display_contracts.short_description = 'Danh sách hợp đồng'
