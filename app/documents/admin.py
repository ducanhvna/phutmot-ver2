from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'google_doc_link')
    search_fields = ('title',)

# Hoặc có thể sử dụng cách đăng ký này nếu bạn không muốn sử dụng decorator
# admin.site.register(Document, DocumentAdmin)
