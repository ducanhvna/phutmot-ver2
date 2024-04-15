
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.home.models import Device, Company
from .utils.core import VanTaiHaHai

from django.contrib.auth.models import User
# Create your views here.
class SyncUserDevice(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        company_id = request.data.get('company_id')
        username = request.data.get('username')
        password = request.data.get('password')
        results = []
        # target_users = User.objects.filter(username=username, password=password)
        # target_user = User.objects.get(username=username) 
        # this checks the plaintext password against the stored hash 
        
        # if user.user_owner :
        #     company_info = user.user_owner.company
        # else:
        company_info = Company.objects.get(pk = company_id)
        apec = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= company_info.username, 
                            password= company_info.password)
        correct = apec.authenticate(username, password) 
        
        if correct > 0:
            try:
                target_user = User.objects.get(username=f'{company_info.code}_{username}')
            except:
                target_user = User.objects.create_user(username=f'{company_info.code}_{username}',
                                    email=f'{company_info.code}_{username}@{company_info.code}.com',
                                    password=f'{company_info.code}_{username}')
            try:
                target_device = target_user.user_device
            except:
                target_device= None
            if not target_device:
                target_device = Device(type = 4, name=f'{company_info.code}_{username}', id=f'{company_info.code}_{username}', 
                        user= target_user)
                target_device.save()
            else:
                target_device = target_user.user_device
            target_device.company = company_info
            target_device.username = username
            target_device.password = password
            target_device.save()
            # target_user= target_users[0]
            current_devices = Device.objects.filter(user=self.request.user)
            for device in current_devices:
    
            # serializer.save(user= user, name=code)
            # user_profile = UserProfile(user_id=user.id,
            #                            affiliate_code=''.join(
            #                                random.choices(string.ascii_uppercase + string.digits, k=8)))
            # user_profile.save()
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
                device.user_owner = target_user
                device.save()
            # if len(current_devices) == 0:
            #     result = {'devices': len(current_devices), 'username': target_user.username}
            # else:
                result_item = {'device_id': device.id,'device_name': device.name, 
                        'owner': device.user_owner.username if device.user_owner else None, 
                        'username': device.user.username if device.user else None}
                results.append(result_item)
            # return Response(device)
        # else:
        #     result = {'result': None}
        # id = request.data.get('id')
        # type = request.data.get('type')
        
        return Response({'data': results})