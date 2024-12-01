from django.views import View
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Customer, Message

class TelegramBotView(View):
    def post(self, request):
        data = request.POST
        telegram_user_id = data['user_id']
        content = data['content']
        customer, created = Customer.objects.get_or_create(telegram_user_id=telegram_user_id)
        Message.objects.create(customer=customer, content=content)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{customer.id}',
            {
                'type': 'chat_message',
                'message': content
            }
        )
        return JsonResponse({'status': 'ok'})
