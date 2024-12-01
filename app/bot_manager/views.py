from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, Message
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
import json


@method_decorator(csrf_exempt, name='dispatch')
class TelegramBotView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))

        if 'message' not in data:
            return HttpResponseBadRequest("Invalid data")

        message_data = data['message']
        telegram_user_id = message_data['from']['id']
        content = message_data.get('text', '')

        if not content:
            return HttpResponseBadRequest("No content to process")

        customer, created = Customer.objects.get_or_create(telegram_user_id=telegram_user_id)
        Message.objects.create(customer=customer, content=content)

        if created:
            welcome_message = "Welcome! We have created a new user for you."
            self.send_message(telegram_user_id, welcome_message)

        try:
            welcome_message = 'hi1'
            self.send_message(telegram_user_id, welcome_message)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{customer.id}',
                {
                    'type': 'chat_message',
                    'message': content
                }
            )

            async_to_sync(channel_layer.group_send)(
                "broadcast",
                {
                    "type": "chat_message",
                    "message": f"This is a broadcast message {content}"
                }
            )

            welcome_message = f'hi {channel_layer}'
            self.send_message(telegram_user_id, welcome_message)
        except Exception as e:
            welcome_message = f'error {e}'
            self.send_message(telegram_user_id, welcome_message)

        return JsonResponse({'status': 'ok'})

    def send_message(self, chat_id, text):
        token = '7681184275:AAFhfoK6NrTASoSzWuzMmV8qkCybh4Ocaaw'
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
        }
        requests.post(url, json=payload)
