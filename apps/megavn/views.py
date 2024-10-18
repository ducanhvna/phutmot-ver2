from django.shortcuts import render
from rest_framework.views import APIView
from .models import MegaEmployee
from rest_framework.response import Response
from django.db.models import Q

import requests
import json

# Create your views here.
class GetListEmployee(APIView):
    def get(self, request, *args, **kwargs): 
        results = []
        for item in MegaEmployee.objects.all():
            results.append({'code': item.code, 
                        'group': item.group, 
                        'department' : item.department, 
                        'name': item.name, 
                        'other' :item.other, 
                        'title' : item.title,
                        'email': item.email,
                        'chat_id': item.chat_id})
        return Response({'data': results})

class ErpProfile(APIView):
    def post(self, request): 
        result = {}
        code = request.data.get('Code')
        results = MegaEmployee.objects.filter(Q(code=code) | 
                    (Q(email=code)&  Q(email__isnull=False)) | \
                    (Q(other=code)&  Q(other__isnull=False))    )
        if len(results)> 0:
            item = results[0]
            
            try:
                url = "https://mbapi.megavietnamgroup.com/api/hr/employees/getprofile"

                payload = json.dumps({
                "Code": item.code
                })
                token = request.data.get('token')
                headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
                }
                
                response = requests.request("POST", url, headers=headers, data=payload)
                response_data = response.json()

                # Extract the data field and convert it back to a dictionary
                if response_data.get("errorCode") == 200:
                    data_str = response_data.get("data")
                    if data_str:
                        data_dict = json.loads(data_str)
                        print(data_dict)
                # print(response.text)
                item.code = code
                item.name = data_dict['FullName']
                item.department = data_dict['DepartmentName']
                item.title = data_dict['JobTitleName']
                if data_dict['WorkEmail']:
                    item.email = data_dict['WorkEmail']
                item.save()
            except Exception as ex:
                print(ex)
                
            
            result = {'EmployeeId': item.code, 
                        'Photo': None, 
                        'DepartmentName' : item.department, 
                        'FullName': item.name, 
                        'DepartmentId' :'', 
                        'JobTitleName' : item.title,
                        'JobTitleId': 0,
                        'HomeEmail': None,
                        'WorkEmail': item.email,
                        'chat_id': item.chat_id}
            try:
                # for change pass
                password = request.data.get('password')
                if item.password != password:
                    item.old_password = item.password
                    item.password = password
                    result['oldPass'] = item.old_password
                item.save()
            except Exception as ex:
                print(ex)
        else:
            try:
                url = "https://mbapi.megavietnamgroup.com/api/hr/employees/getprofile"

                payload = json.dumps({
                "Code": item.code
                })
                token = request.data.get('token')
                headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
                }
                
                response = requests.request("POST", url, headers=headers, data=payload)
                response_data = response.json()

                # Extract the data field and convert it back to a dictionary
                if response_data.get("errorCode") == 200:
                    data_str = response_data.get("data")
                    if data_str:
                        data_dict = json.loads(data_str)
                        print(data_dict)
                if(data_dict):
                # print(response.text)
                    item = MegaEmployee(
                        code = code,
                        name = data_dict['FullName'],
                        department = data_dict['DepartmentName'],
                        title = data_dict['JobTitleName'])
                    if data_dict['WorkEmail'] and item:
                        item.email = data_dict['WorkEmail']
                    item.save()
                    
                    result = {'EmployeeId': item.code, 
                        'Photo': None, 
                        'DepartmentName' : item.department, 
                        'FullName': item.name, 
                        'DepartmentId' :'', 
                        'JobTitleName' : item.title,
                        'JobTitleId': 0,
                        'HomeEmail': None,
                        'WorkEmail': item.email,
                        'chat_id': item.chat_id}
            except Exception as ex:
                print(ex)
            
            
        return Response({'data': result})

class ErpLink(APIView):
    def post(self, request): 
        # result = {}
        email = request.data.get('email')
        password = request.data.get('password')
        chat_id = request.data.get('chat_id')
        
        results = MegaEmployee.objects.filter(Q(code=email) )
        # | \
        #             (Q(email=email) &  Q(email__isnull=False)) | \
        #             (Q(other=email) &  Q(other__isnull=False)))
        result = {}
        for item in results:
            try:
                item.chat_id = chat_id
                try:
                    deviceToken = request.data.get('deviceToken')
                    if (deviceToken):
                        item.device_token = deviceToken
                except Exception as ex:
                    print(ex)
                if password:
                    if password != item.password:
                        item.old_password = item.password
                        item.password = password
                item.save()
                result = {'EmployeeId': item.code, 
                        'Photo': None, 
                        'DepartmentName' : item.department, 
                        'FullName': item.name, 
                        'DepartmentId' :'', 
                        'JobTitleName' : item.title,
                        'JobTitleId': 0,
                        'HomeEmail': None,
                        'WorkEmail': item.email,
                        'chat_id': item.chat_id}
            except Exception as ex2:
                print(ex2)
        return Response({'data': result})

class getDeviceToken(APIView):
    def post(self, request): 
        # result = {}
        email = request.data.get('email')
        password = request.data.get('password')
        # chat_id = request.data.get('chat_id')
        # deviceToken = request.data.get('deviceToken')
        results = MegaEmployee.objects.filter(Q(code=email) & Q(email__isnull=False))
        # | \
        #             (Q(email=email) &  Q(email__isnull=False)) | \
        #             (Q(other=email) &  Q(other__isnull=False)))
        # for item in results:
        #     item.chat_id = chat_id
        #     if (deviceToken):
        #         item.device_token = deviceToken
        #     if password:
        #         item.password = password
        #     item.save()
        if len(results)>0:
            return Response({'deviceToken': results[0].device_token})
        else:
            return Response({'deviceToken': None})