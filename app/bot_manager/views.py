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
from .models import Setting, Chatuser, Story, Like
from .serializers import SettingSerializer, ChatuserSerializer, CommonResponseSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import QueryDict
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Post, Room, FollowingList, Comment
from .serializers import FeedSerializer, RoomSerializer, StorySerializer, PostSerializer, CommentSerializer
import random


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

        # Check if there's a user in the request
        if request.user and request.user.is_authenticated:
            # Case 1: User is logged in
            user = request.user
            message = 'User is logged in. Processing with existing user.'

        # Case 2: No user is logged in
        identity = data.get('identity')
        device_token = data.get('device_token')
        login_type = data.get('login_type')
        device_type = data.get('device_type')

        user, created = Chatuser.objects.get_or_create(
            identity=identity,
            defaults={
                'device_token': device_token,
                'login_type': login_type,
                'device_type': device_type
            }
        )

        message = 'Chatuser added successfully' if created else 'Chatuser already exists, data updated'

        if not created:
            user.device_token = device_token
            user.login_type = login_type
            user.device_type = device_type
            user.save()

        serializer = ChatuserSerializer(user)
        response_data = {
            'status': True,
            'message': message,
            'data': serializer.data
        }
        status_code = status.HTTP_201_CREATED if 'created' in locals() and created else status.HTTP_200_OK
        return Response(response_data, status=status_code)


class FetchProfileView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        # my_user_id = request.data.get('my_user_id')
        user_id = request.data.get('user_id')

        user = get_object_or_404(Chatuser, id=user_id)
        serializer = ChatuserSerializer(user)
        response_data = {
            'status': True,
            'message': 'Chatuser profile fetched successfully',
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

        user = get_object_or_404(Chatuser, id=user_id)

        if interest_ids:
            if isinstance(interest_ids, str):
                interest_ids = json.loads(interest_ids)  # Convert string to list if needed
            user.interest_ids = ','.join(map(str, interest_ids)) if isinstance(interest_ids, list) else str(interest_ids)

        if username:
            user.username = username

        user.save()

        serializer = ChatuserSerializer(user)
        response_data = {
            'status': True,
            'message': 'Chatuser profile updated successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CheckUsernameView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        username = request.data.get('username')
        if Chatuser.objects.filter(username=username).exists():
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
        # Convert limit to an integer
        limit = int(request.data.get('limit', 100))
        should_send_suggested_room = request.data.get('should_send_suggested_room', 1)

        # Lấy danh sách các bài viết của người dùng
        following_list = FollowingList.objects.filter(my_user_id=my_user_id).values_list('user_id', flat=True)
        posts = []
        try:
            posts = Post.objects.filter(user_id__in=following_list).order_by('-created_at')[:limit]
        except Exception as ex:
            print(ex)
        if len(posts) < 1:
            posts = Post.objects.filter(user_id=my_user_id).order_by('-created_at')[:limit]

        feed_serializer = FeedSerializer(posts, many=True)
        response_message = "Fetched posts successfully"

        # Add new post if client is authenticated
        if request.user and request.user.is_authenticated:
            new_post_data = {
                'user_id': request.user.id,
                'desc': f"Post by {request.user.username}",
                'tags': 'new,post,tags',
                'comments_count': 0,
                'likes_count': 0,
                'created_at': timezone.now(),  # Ensure datetime fields match structure
                'updated_at': timezone.now()
            }

            # Serialize the new post data
            new_post_serializer = FeedSerializer(data=new_post_data)
            if new_post_serializer.is_valid():
                feed_serializer.data.append(new_post_serializer.data)
                response_message = "Fetched posts with user details successfully"
            else:
                print("New post data invalid:", new_post_serializer.errors)
                response_message = "Fetched posts successfully with some errors in additional post"
        else:
            response_message = "Fetched posts successfully"

        response_data = {
            'status': True,
            'message': response_message,
            'data': feed_serializer.data,
            'suggestedRooms': []
        }

        if should_send_suggested_room:
            suggested_rooms = Room.objects.all()
            room_serializer = RoomSerializer(suggested_rooms, many=True)
            response_data['suggestedRooms'] = room_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)


class FetchPostByUserView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        user_id = request.data.get('user_id')
        start = int(request.data.get('start', 0))
        limit = int(request.data.get('limit', 20))

        # Fetch posts by user_id
        posts = []
        try:
            posts = Post.objects.filter(user_id=user_id).order_by('-created_at')[start:start + limit]
        except Exception as ex:
            print(ex)
        if len(posts) < 1:
            posts = Post.objects.filter(user_id=user_id).order_by('-created_at')[:limit]
        feed_serializer = FeedSerializer(posts, many=True)

        response_message = "Fetched posts successfully"

        # Add new post if client is authenticated
        if request.user and request.user.is_authenticated:
            new_post_data = {
                'user_id': request.user.id,
                'desc': f"Post by {request.user.username}",
                'tags': 'new,post,tags',
                'comments_count': 0,
                'likes_count': 0,
                'created_at': timezone.now(),  # Ensure datetime fields match structure
                'updated_at': timezone.now()
            }

            # Serialize the new post data
            new_post_serializer = FeedSerializer(data=new_post_data)
            if new_post_serializer.is_valid():
                feed_serializer.data.append(new_post_serializer.data)
                response_message = "Fetched posts with user details successfully"
            else:
                print("New post data invalid:", new_post_serializer.errors)
                response_message = "Fetched posts successfully with some errors in additional post"
        else:
            response_message = "Fetched posts successfully"

        response_data = {
            'status': True,
            'message': response_message,
            'data': feed_serializer.data,
            'suggestedRooms': []
        }

        return Response(response_data, status=status.HTTP_200_OK)


class FetchStoryView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        my_user_id = request.data.get('my_user_id')

        # Validate the user
        try:
            Chatuser.objects.get(id=my_user_id)
        except Chatuser.DoesNotExist:
            return Response({'error': 'Chatuser does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch stories
        stories = Story.objects.filter(user_id=my_user_id)
        story_serializer = StorySerializer(stories, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched stories successfully',
            'data': story_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AddPostView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        desc = request.data.get('desc')
        tags = request.data.get('tags', '')
        user_id = request.data.get('user_id')
        content_type = request.data.get('content_type')

        # Validate required fields
        if not desc or not user_id or not content_type:
            return Response({'error': 'desc, user_id, and content_type are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new post
        post_data = {
            'desc': desc,
            'tags': tags,
            'user_id': user_id,
            'content_type': content_type,
        }
        post_serializer = PostSerializer(data=post_data)

        if post_serializer.is_valid():
            post_serializer.save()
            response_data = {
                'status': True,
                'message': 'Post created successfully',
                'data': post_serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchCommentsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        post_id = request.data.get('post_id')

        # Validate the post_id
        if not post_id:
            return Response({'error': 'post_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch comments for the given post_id
        comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        comment_serializer = CommentSerializer(comments, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched comments successfully',
            'data': comment_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class LikePostView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')

        # Validate required fields
        if not user_id or not post_id:
            return Response({'status': False, 'message': 'user_id and post_id are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the like already exists
        if Like.objects.filter(user_id=user_id, post_id=post_id).exists():
            return Response({'status': True, 'message': 'Like already exists'}, status=status.HTTP_200_OK)

        # Create a new like
        Like.objects.create(user_id=user_id, post_id=post_id)
        return Response({'status': True, 'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)


class DislikePostView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')

        # Validate required fields
        if not user_id or not post_id:
            return Response({'status': False, 'message': 'user_id and post_id are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the like exists
        like = Like.objects.filter(user_id=user_id, post_id=post_id).first()
        if like:
            like.delete()
            return Response({'status': True, 'message': 'Post disliked successfully'}, status=status.HTTP_200_OK)

        return Response({'status': True, 'message': 'Like does not exist'}, status=status.HTTP_200_OK)


class CreateStoryView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        user_id = request.data.get('user_id')
        story_type = request.data.get('type')
        duration = request.data.get('duration')
        content = request.data.get('content', '-')

        # Validate required fields
        if not user_id or story_type is None or duration is None:
            return Response({'status': False, 'message': 'user_id, type, and duration are required fields'}, status=status.HTTP_400_BAD_REQUEST)
        # Ensure content is a valid string and set default if necessary
        if not isinstance(content, str) or not content:
            content = '-'
        # Create a new story
        story_data = {
            'user_id': user_id,
            'type': story_type,
            'duration': duration,
            'content': content,
        }
        story_serializer = StorySerializer(data=story_data)

        if story_serializer.is_valid():
            story_serializer.save()
            response_data = {
                'status': True,
                'message': 'Story created successfully',
            }
            response_serializer = CommonResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(story_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchRandomRoomsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        limit = int(request.data.get('limit', 20))
        user_id = request.data.get('user_id')

        # Validate required fields
        if user_id is None:
            return Response({'status': False, 'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch random rooms
        rooms = list(Room.objects.all())
        random.shuffle(rooms)
        rooms = rooms[:limit]

        room_serializer = RoomSerializer(rooms, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched random rooms successfully',
            'data': room_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class LogOutView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        response_data = {
            'status': True,
            'message': 'Story created successfully',
        }
        response_serializer = CommonResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
