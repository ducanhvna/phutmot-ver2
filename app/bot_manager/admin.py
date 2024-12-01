from django.contrib import admin
from .models import Customer, Message


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram_user_id')
    search_fields = ('name', 'telegram_user_id')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'content', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('customer__name', 'content')
