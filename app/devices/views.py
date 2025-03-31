import random
import string
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from .models import Device
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny


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

        # Tạo JWT token (sử dụng thư viện rest_framework_simplejwt)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'username': user.username
        })
