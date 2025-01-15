from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Customer, Message
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Setting, User
from .serializers import SettingSerializer, UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import QueryDict
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Post, Room, FollowingList
from .serializers import FeedSerializer, RoomSerializer


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


@method_decorator(csrf_exempt, name='dispatch')
class FetchSettingView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            setting = Setting.objects.first()  # Assuming there's only one settings object
            if setting:
                serializer = SettingSerializer(setting)
                return Response({"status": True, "message": "Settings fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "message": "No settings found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class AddUserView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        data = request.data
        identity = data.get('identity')
        device_token = data.get('device_token')
        login_type = data.get('login_type')
        device_type = data.get('device_type')

        user, created = User.objects.get_or_create(
            identity=identity,
            defaults={
                'device_token': device_token,
                'login_type': login_type,
                'device_type': device_type
            }
        )

        if not created:
            user.device_token = device_token
            user.login_type = login_type
            user.device_type = device_type
            user.save()

        serializer = UserSerializer(user)
        response_data = {
            'status': True,
            'message': 'User added successfully' if created else 'User already exists, data updated',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class FetchProfileView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        # my_user_id = request.data.get('my_user_id')
        user_id = request.data.get('user_id')

        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        response_data = {
            'status': True,
            'message': 'User profile fetched successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class EditProfileView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        user_id = request.data.get('user_id')
        interest_ids = request.data.get('interest_ids', None)
        username = request.data.get('username', None)

        user = get_object_or_404(User, id=user_id)

        if interest_ids:
            if isinstance(interest_ids, str):
                interest_ids = json.loads(interest_ids)  # Convert string to list if needed
            user.interest_ids = ','.join(map(str, interest_ids)) if isinstance(interest_ids, list) else str(interest_ids)

        if username:
            user.username = username

        user.save()

        serializer = UserSerializer(user)
        response_data = {
            'status': True,
            'message': 'User profile updated successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CheckUsernameView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            response_data = {
                'status': False,
                'message': 'Username exists'
            }
        else:
            response_data = {
                'status': True,
                'message': 'Username does not exist'
            }

        return Response(response_data, status=status.HTTP_200_OK)


class FetchPostsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        my_user_id = request.data.get('my_user_id')
        limit = request.data.get('limit', 100)
        should_send_suggested_room = request.data.get('should_send_suggested_room', 1)

        # Lấy danh sách các bài viết của người dùng
        following_list = FollowingList.objects.filter(my_user_id=my_user_id).values_list('user_id', flat=True)
        posts = Post.objects.filter(user_id__in=following_list).order_by('-created_at')[:limit]
        feed_serializer = FeedSerializer(posts, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched posts successfully',
            'data': feed_serializer.data,
        }

        if should_send_suggested_room:
            suggested_rooms = Room.objects.all()
            room_serializer = RoomSerializer(suggested_rooms, many=True)
            response_data['suggestedRooms'] = room_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
