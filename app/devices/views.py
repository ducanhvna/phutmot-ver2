import random
import string
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from .models import Device
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from bot_manager.models import Room
from django.utils import timezone
from rest_framework import status
from bot_manager.serializers import RoomSerializer
from .serializers import ProductCategorySerializer


# Hàm tạo mã code random
def generate_random_username():
    while True:
        # Mã bắt đầu bằng chữ hoa, tiếp theo là 7 ký tự chữ hoa hoặc số
        code = random.choice(string.ascii_uppercase) + ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=7)
        )
        # Kiểm tra xem mã này đã tồn tại trong User chưa
        if not User.objects.filter(username=code).exists():
            return code


@method_decorator(csrf_exempt, name='dispatch')
class DeviceLoginView(APIView):
    authentication_classes = []  # Bỏ qua xác thực cho endpoint này
    permission_classes = (AllowAny,)

    def post(self, request):
        device_id = request.data.get('device_id')
        device_name = request.data.get('device_name')
        os_version = request.data.get('os_version')
        platform = request.data.get('platform')

        if not all([device_id, device_name, os_version]):
            return Response({'error': 'Missing device information'}, status=400)

        # Kiểm tra xem device đã tồn tại chưa
        device, created = Device.objects.get_or_create(device_id=device_id, defaults={
            'device_name': device_name,
            'os_version': os_version,
        })

        # Kiểm tra user liên kết với device hoặc tạo mới user
        if not device.user:
            # Tạo mã username độc nhất
            username = generate_random_username()
            user = User.objects.create(username=username)
            device.user = user
            device.save()
        else:
            user = device.user
        info = device.info
        if info.get('platform', '') != platform:
            info['platform'] = platform
            device.info = info
            device.save()
        # Tạo JWT token (sử dụng thư viện rest_framework_simplejwt)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'username': user.username
        })


class FetchRoomChatsView(APIView):
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

        if request.user and request.user.is_authenticated:
            print('auth')
            pass
            # rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list

        else:
            new_room_data = {
                'id': 9000,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Phòng khám đông y phúc thành (Sức khỏe) ',
                'desc': 'New room added for authenticated user',
                'interest_ids': '1,2,3',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = user_id  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list

            new_room_data = {
                'id': 9001,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Địa lý 10 - Kiến thức tổng quát (Education)',
                'desc': 'New room added for authenticated user',
                'interest_ids': '1,2,3',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = user_id  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(1, new_room_data_serialized)  # Add the new room to the beginning of the list

            new_room_data = {
                'id': 9002,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Studio Đức Hollywood (Galery)',
                'desc': 'New room added for authenticated user',
                'interest_ids': '7,8',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_instance.user_room_status = 5
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = user_id  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(2, new_room_data_serialized)  # Add the new room to the beginning of the list
            new_room_data = {
                'id': 9003,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Pamo co.,Ltd (Gallery)',
                'desc': 'New room added for authenticated user',
                'interest_ids': '7,8',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_instance.user_room_status = 5
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = user_id  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(3, new_room_data_serialized)  # Add the new room to the beginning of the list
            new_room_data = {
                'id': 9003,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Phòng khám Tâm Đức (Sức Khỏe)',
                'desc': 'New room added for authenticated user',
                'interest_ids': '7,8',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_instance.user_room_status = 5
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = user_id  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(4, new_room_data_serialized)  # Add the new room to the beginning of the list
        room_serializer = RoomSerializer(rooms, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched random rooms successfully',
            'data': room_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class FetchUserChatsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        limit = int(request.data.get('limit', 20))

        # Fetch random rooms
        rooms = list(Room.objects.all())
        random.shuffle(rooms)
        rooms = rooms[:limit]

        if request.user and request.user.is_authenticated:
            print('auth')
            pass
            # rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list

        else:
            new_room_data = {
                'id': 9010,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Hồ sơ cá nhân ',
                'desc': 'New room added for authenticated user',
                'interest_ids': '1,2,3',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = 0  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list

            new_room_data = {
                'id': 9011,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Gia đình',
                'desc': 'Thông tin cá nhân vợ, chồng, con cái',
                'interest_ids': '1,2,3',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = 0  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(1, new_room_data_serialized)  # Add the new room to the beginning of the list

            new_room_data = {
                'id': 9012,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Bạn bè',
                'desc': 'Gia đình hai bên nội ngoại',
                'interest_ids': '7,8',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_instance.user_room_status = 5
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = 0  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(2, new_room_data_serialized)  # Add the new room to the beginning of the list
            new_room_data = {
                'id': 9013,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Các mối quan hệ khác',
                'desc': 'New room added for authenticated user',
                'interest_ids': '7,8',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_instance.user_room_status = 5
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = 0  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(3, new_room_data_serialized)  # Add the new room to the beginning of the list

        room_serializer = RoomSerializer(rooms, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched random rooms successfully',
            'data': room_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProductCategoryAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request, *args, **kwargs):
        raw_data = {
            'PHOTOBOOK_MOCONG_15X15': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOCONG_20X20': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOCONG_25X25': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOCONG_30X30': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOPHANG_15X15': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOPHANG_20X20': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOPHANG_25X25': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
            'PHOTOBOOK_MOPHANG_30x30': {'ToiDa': 10, 'ThemTrang': 10, 'KhoiTaoThemTrang': 12, 'GiaTrang': 12, 'GiaBan': 10, 'Indi_ID_Trang': 10, 'Indi_ID': 10, 'so_trang_mac_dinh': 10},
        }
        serialized_data = {key: ProductCategorySerializer(value).data for key, value in raw_data.items()}
        response_data = {
            'status': True,
            'message': 'Fetched random rooms successfully',
            'data': serialized_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PriceAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request, *args, **kwargs):
        raw_data = {
            'price': 100
        }
        response_data = {
            'status': True,
            'message': 'Fetched Price successfully',
            'data': raw_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class fetchRoomDetailView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def post(self, request):
        limit = int(request.data.get('limit', 20))
        room_id = int(request.data.get('room_id', 0))
        # Fetch random rooms
        rooms = list(Room.objects.all())
        random.shuffle(rooms)
        rooms = rooms[:limit]

        if request.user and request.user.is_authenticated:
            print('auth')
            pass
            # rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list

        else:
            new_room_data = {
                'id': room_id,
                'admin_id': 0,
                'photo': 'default_photo_url',  # Replace this with a real photo URL
                'title': 'Hồ sơ cá nhân ',
                'desc': 'New room added for authenticated user',
                'interest_ids': '1,2,3',  # Replace with real interest data
                'is_private': 0,
                'is_join_request_enable': 1,
                'total_member': 1,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }

            new_room_instance = Room(**new_room_data)
            new_room_serializer = RoomSerializer(new_room_instance)
            new_room_data_serialized = new_room_serializer.data
            new_room_data_serialized['private_user_id'] = 0  # Add private_user_id directly in serialized data
            new_room_data_serialized['userRoomStatus'] = 5
            rooms.insert(0, new_room_data_serialized)  # Add the new room to the beginning of the list
            # rooms.insert(0, new_room_instance)  # Add the new room to the beginning of the list
            rooms.insert(3, new_room_data_serialized)  # Add the new room to the beginning of the list

        room_serializer = RoomSerializer(rooms, many=True)

        response_data = {
            'status': True,
            'message': 'Fetched room detail successfully',
            'data': room_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
