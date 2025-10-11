# backend/apps/core/asgi.py

import os
import django

# Set settings module *TRƯỚC* khi setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Khởi tạo Django
django.setup()

# IMPORT Channels và các thành phần khác *SAU* khi setup Django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import websocket routes *SAU* khi Django được cấu hình
from apps.home.routing import websocket_urlpatterns

# Định nghĩa Application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})