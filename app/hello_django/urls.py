from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from upload.views import image_upload
from bot_manager.views import TelegramBotView
from bot_manager.routing import websocket_urlpatterns

urlpatterns = [
    path("", include("apps.authentication.urls")),  # Auth routes - login / register
    path('', include('home.urls')),
    path("upload/", image_upload, name="upload"),
    path("admin/", admin.site.urls),
    path("telegram/webhook/", TelegramBotView.as_view(), name="telegram_webhook"),
    re_path(r'^ws/', include(websocket_urlpatterns)),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
