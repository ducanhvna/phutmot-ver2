from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Customer, Message

class TelegramBotView(View):
    def post(self, request):
        data = request.POST

        # Kiểm tra các trường bắt buộc
        if 'user_id' not in data or 'content' not in data:
            return HttpResponseBadRequest("Missing required fields: 'user_id' and/or 'content'")

        telegram_user_id = data['user_id']
        content = data['content']

        # Xử lý tin nhắn
        customer, created = Customer.objects.get_or_create(telegram_user_id=telegram_user_id)
        Message.objects.create(customer=customer, content=content)
        # Gửi tin nhắn qua WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{customer.id}',
            {
                'type': 'chat_message',
                'message': content
            }
        )
        return JsonResponse({'status': 'ok', 'created': created})
