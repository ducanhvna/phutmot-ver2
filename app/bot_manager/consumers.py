import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # if isinstance(self.scope['user'], AnonymousUser):
        #     await self.close()
        # else:
        # Thêm người dùng vào nhóm broadcast
        await self.channel_layer.group_add("broadcast", self.channel_name)

        self.room_group_name = 'chat_%s' % self.scope['user'].id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Loại bỏ người dùng khỏi nhóm broadcast
        await self.channel_layer.group_discard("broadcast", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("receive: ", text_data_json)
        # message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data_json
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
