from django.contrib import admin
from .models import Book


@admin.register(Book)
class Company(admin.ModelAdmin):
    list_display = ('db', 'url', 'username', 'password', 'company_name')
    search_fields = ('company_code', 'author')
