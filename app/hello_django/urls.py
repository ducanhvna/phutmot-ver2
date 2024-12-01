from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from upload.views import image_upload
from bot_manager.views import TelegramBotView

urlpatterns = [
    path("", image_upload, name="upload"),
    path("admin/", admin.site.urls),
    path("telegram/webhook/", TelegramBotView.as_view(), name="telegram_webhook"),
    path("ws/", include("bot_manager.routing")),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
