# backend/apps/home/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QRSignalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # join the same group your view sends to
        self.room_group_name = "qr_pad"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"Nhận được từ client: {text_data}")
        try:
            data = json.loads(text_data or "{}")
        except Exception:
            data = {}
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'qr_message',
                'message': data.get('message', '')
            }
        )

    async def qr_message(self, event):
        # called when group_send sends {'type':'qr_message', 'message': ...}
        await self.send(text_data=json.dumps({
            'message': event.get('message')
        }))
