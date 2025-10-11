from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Thử bỏ ký tự kết thúc '$' để khớp mọi thứ bắt đầu bằng 'ws/qr/'
    re_path(r'ws/qr/', consumers.QRSignalConsumer.as_asgi()), 
]
