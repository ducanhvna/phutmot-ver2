from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.home.models import Device, Company
from .unity import Apec
from django.conf import settings

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
        company_info = Company.objects.get(url = settings.APEC_CONFIG['SERVER_URL'])
        apec = Apec(settings.APEC_CONFIG['SERVER_URL'], settings.APEC_CONFIG['SERVER_URL_DB'],
                settings.APEC_CONFIG['SERVER_USERNAME'], settings.APEC_CONFIG['SERVER_PASSWORD'])
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

class GetListHrmEmployees(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs): 
        user = request.user 
        device = user.user_device
        results = []

        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        # target_users = User.objects.filter(username=username, password=password)
        # target_user = User.objects.get(username=username) 
        # this checks the plaintext password against the stored hash 
        
        # if user.user_owner :
        #     company_info = user.user_owner.company
        # else:
        # company_info = Company.objects.get(pk = company_id)
        # apec = Apec(company_info.url, company_info.dbname, company_info.username, company_info.password)
        username = device.username
        password = device.password
        apec = Apec(company_info.url, company_info.dbname, username, password)
        
        results = apec.getlistemployee()
        # if apec.uid > 0:
        #     for item in apec.getlistemployee():
        #         if item:
        #             results.append({'id': item[0] if item[0] else None, 'name': item[1] if item[1] else None})    
        return Response({'data': results})

class GetListHrmAttendanceReport(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        try:
            date_str = request.data.get('date') 
        except:
            date_str = None
        user = request.user 
        device = user.user_device
        results = []

        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        # target_users = User.objects.filter(username=username, password=password)
        # target_user = User.objects.get(username=username) 
        # this checks the plaintext password against the stored hash 
        
        # if user.user_owner :
        #     company_info = user.user_owner.company
        # else:
        # company_info = Company.objects.get(pk = company_id)
        # apec = Apec(company_info.url, company_info.dbname, company_info.username, company_info.password)
        username = device.username
        password = device.password
        apec = Apec(company_info.url, company_info.dbname, username, password)
        
        results = apec.getattendancereport(date_str)
        # if apec.uid > 0:
        #     for item in apec.getlistemployee():
        #         if item:
        #             results.append({'id': item[0] if item[0] else None, 'name': item[1] if item[1] else None})    
        return Response({'data': results})

class GetListTask(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = request.user 
        device = user.user_device
        results = []

        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        # company_info = device.company
        # target_users = User.objects.filter(username=username, password=password)
        # target_user = User.objects.get(username=username)
        # this checks the plaintext password against the stored hash

        # if user.user_owner :
        #     company_info = user.user_owner.company
        # else:
        # company_info = Company.objects.get(pk = company_id)
        # apec = Apec(company_info.url, company_info.dbname, company_info.username, company_info.password)
        username = device.username
        password = device.password
        apec = Apec(
            settings.APEC_CONFIG["SERVER_URL"],
            settings.APEC_CONFIG["SERVER_URL_DB"],
            username,
            password,
        )

        results = apec.getlistTask()
        # if apec.uid > 0:
        #     for item in apec.getlistemployee():
        #         if item:
        #             results.append({'id': item[0] if item[0] else None, 'name': item[1] if item[1] else None})
        return Response({'data': results})

class GetListCompany(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs): 
        user = request.user 
        device = user.user_device
        results = []

        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        # target_users = User.objects.filter(username=username, password=password)
        # target_user = User.objects.get(username=username) 
        # this checks the plaintext password against the stored hash 
        
        # if user.user_owner :
        #     company_info = user.user_owner.company
        # else:
        # company_info = Company.objects.get(pk = company_id)
        # apec = Apec(company_info.url, company_info.dbname, company_info.username, company_info.password)
        username = device.username
        password = device.password
        apec = Apec(company_info.url, company_info.dbname, username, password)
        
        results = []
        if apec.uid > 0:
            for item in apec.GetListCompany():
                if item:
                    results.append({'id': item[0] if item[0] else None, 'name': item[1] if item[1] else None})
            
        return Response({'data': results})
