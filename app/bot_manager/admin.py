from django.contrib import admin
from .models import Customer, Message, Interest, Chatuser, Post


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram_user_id')
    search_fields = ('name', 'telegram_user_id')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'content', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('customer__name', 'content')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(Chatuser)
class ChatuserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'profile')
    list_filter = ('username',)
    search_fields = ('username',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'desc', 'tags', 'created_at')
    list_filter = ('user_id', 'desc')
    search_fields = ('user_id', 'desc')
