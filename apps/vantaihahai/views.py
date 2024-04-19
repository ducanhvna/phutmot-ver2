
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.home.models import Device, Company
from .utils.core import VanTaiHaHai, GetThongtintaixe, tatcachuyendicuataixe, chitiethanhtrinh, \
    danhsachtatcaxe, tatcamathang, thongtinxe, danhsachyeucaubaotrixe, capnhatghichubaotri, \
    danhsachcacphuongtheohuyen, danhsachcachuyentheotinh, danhsachcactinh, tatcadiadiem, themmoichuyendi

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
        vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
        
        if vantai.uid > 0:
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
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
        
        results = []
            
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
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
        results = []
        return Response({'data': results})
    
class GetListHrmAttendanceReport(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs): 
        user = request.user 
        device = user.user_device
        results = []

        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
        results = []
        return Response({'data': results})

class ThongtintaixeApi(APIView):
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        
        try:
            # user = self.request.user 
            devices = Device.objects.filter(user=self.request.user)
            print("danh sach : ",devices)
            # device = user.user_device
            if len(devices)>0:
                device = devices[0]
                if device.user_owner:
                    owner_devices = Device.objects.filter(user=device.user_owner)
                    if len(owner_devices)>0:
                        device = owner_devices[0]
            # if device:
                user = request.user 
                device = user.user_device
                results = []

                user_owner = device.user_owner
                if user_owner:
                    device = user_owner.user_device
                company_info = device.company
                username = device.username
                password = device.password
                vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
                data = GetThongtintaixe(vantai.uid)
                data['data']['code'] = device.name
                # salaries = MemberSalary.objects.filter(member = device.device_membership.member)
                # ls = []
                # for item in salaries:
                #     ls.append({'date':item.date, 'salary':item.salary})
                # data['data']['salary'] = ls

                return Response(data)

            return Response({
                            'status': False, 
                            'error' : "You does not own any device, please create a new one"
                        })
        except Exception as ex:
            print(ex)
            return Response({
                            'status': False, 
                            'error' : "You does not own any device, please create a new one"
                        })
            
class Tatcachuyendi(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        # try:
        queryset = []
        results= []
        # find device
        devices = Device.objects.filter(user=self.request.user)

        if len(devices)>0:
            device = devices[0]
            if device.user_owner:
                owner_devices = Device.objects.filter(user=device.user_owner)
                if len(owner_devices)>0:
                    device = owner_devices[0]
                company_info = device.company
                username = device.username
                password = device.password
                vantai = VanTaiHaHai(url=company_info.url, 
                            dbname= company_info.dbname,
                            username= username, 
                            password= password)
                
                queryset2= vantai.tatcachuyendicuataixe()
                employee_id = queryset2['employee']['id']
                print("Tat ca cac chuyen di cua: ", employee_id)
            
                queryset= tatcachuyendicuataixe(employee_id)
                for item in queryset['data']['results']:
                    for item2 in queryset2['data']['results']:
                        if (item['id'] == item2['id']):
                            item['location_id'] = item2['location_id']
                            item['location_dest_id'] = item2['location_dest_id']
                            item['fleet_product_id'] = item2['fleet_product_id']
                print(queryset)
        return Response(queryset)
        # except Exception as ex:
        #     print(ex)
        #     return Response({
        #                     'status': False, 
        #                     'error' : "You does not own any device, please create a new one"
        #                 })

class Cacchuyenhomnay(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        queryset = []
        result= []
        # find device
        # devices = Device.objects.filter(user=self.request.user)
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        username = device.username
        password = device.password
        company_info = device.company
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.tatcachuyendihomnay()
            # except Exception as ex:
            #     print(ex)
            #     return Response({
            #                     'status': False, 
            #                     'error' : "You does not own any device, please create a new one"
            #                 })
        return Response(result)


class CapnhatHanghoa(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def put(self, request, *args, **kwargs): 
        hanhtrinh = kwargs.get('hanhtrinh')
        product_id = request.data.get('product_id')
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.capnhathanghoa(hanhtrinh, product_id)
    
        return Response(result)    

class CapnhatkmKetthuc(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def put(self, request, *args, **kwargs): 
        hanhtrinh = kwargs.get('hanhtrinh')
        km_end = request.data.get('km')
        url = request.data.get('url')
        # attackements = request.data.get('attackements')
        attackements = [url]
        # ht_object = Hanhtrinh.objects.get(hanhtrinh_id=hanhtrinh)
        # ht_object.odo_end= km_end
        # ht_object.save()
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        username = device.username
        password = device.password
        company_info = device.company
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.capnhatsokmketthuchanhtrinh(hanhtrinh, km_end, None, attackements)
            # attachments = body['attachments']
            # for item in attachments:
            #     atts= AttackmentHanhTrinh.objects.filter(hanhtrinh = ht_object, url=item)
            #     if len(atts) == 0:
            #         att = AttackmentHanhTrinh(hanhtrinh = ht_object, url= item)
            #         att.save()

        # result = chitiethanhtrinh(hanhtrinh)
        # result['data']['sid'] = result['data']['id']
        # result['data']['id'] = ht_object.pk
        return Response(result)
        # except Exception as ex:
        #     print(ex)
        #     return Response({
        #                     'status': False, 
        #                     'error' : "You does not own any device, please create a new one"
        #                 })
        #     vantai = VanTaiHaHai()
        #     vantai.capnhatsokmketthuchanhtrinh(hanhtrinh.hanhtrinh_id, odo_end, body, attackements)
        #     return HttpResponseRedirect('/vantai/chitiethanhtrinh/{}/'.format(hanhtrinh.id))

        # context = self.get_context_data(form=form)
        # return self.render_to_response(context)     
    # def get_context_data(self, **kwargs):
    #     """Overide get_context_data method
    #     """
        
    #     context = super(CapnhatKetthucHanhtrinhView, self).get_context_data(**kwargs)
    #     hanhtrinh_pk = self.kwargs['pk']
    #     hanhtrinh = Hanhtrinh.objects.get(pk=hanhtrinh_pk)
    #     form = KmHanhtrinhForm(initial={'name':f"End-{hanhtrinh.hanhtrinh_id}",'odo':None,'hanhtrinh': hanhtrinh})  # instance= None

    #     context["form"] = form
    #     #context["latest_article"] = latest_article

    #     return context
    # def get(self, request, *args, **kwargs):
    #     return self.post(request, *args, **kwargs)
class CapnhatDiadiemBatdau(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def put(self, request, *args, **kwargs): 
        hanhtrinh = kwargs.get('hanhtrinh')
        location_id = request.data.get('location_id')
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        username = device.username
        password = device.password
        company_info = device.company
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.capnhatlocationbatdauhanhtrinh(hanhtrinh, location_id)
            # attachments = body['attachments']
            # for item in attachments:
            #     atts= AttackmentHanhTrinh.objects.filter(hanhtrinh = ht_object, url=item)
            #     if len(atts) == 0:
            #         att = AttackmentHanhTrinh(hanhtrinh = ht_object, url= item)
            #         att.save()
        # result = chitiethanhtrinh(hanhtrinh)
        # result['data']['sid'] = result['data']['id']
        # result['data']['id'] = ht_object.pk
        return Response(result)
class CapnhatDiadiemKetthuc(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def put(self, request, *args, **kwargs): 
        hanhtrinh = kwargs.get('hanhtrinh')
        location_id = request.data.get('location_id')
        # ht_object = Hanhtrinh.objects.get(hanhtrinh_id=hanhtrinh)
        # ht_object.odo_start= km_end
        # ht_object.save()
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        username = device.username
        password = device.password
        

        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.capnhatlocationketthuchanhtrinh(hanhtrinh, location_id)
            # attachments = body['attachments']
            # for item in attachments:
            #     atts= AttackmentHanhTrinh.objects.filter(hanhtrinh = ht_object, url=item)
            #     if len(atts) == 0:
            #         att = AttackmentHanhTrinh(hanhtrinh = ht_object, url= item)
            #         att.save()
        # result = chitiethanhtrinh(hanhtrinh)
        # result['data']['sid'] = result['data']['id']
        # result['data']['id'] = ht_object.pk
        return Response(result)
class CapnhatkmBatdau(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def put(self, request, *args, **kwargs): 
        hanhtrinh = kwargs.get('hanhtrinh')
        km_end = request.data.get('km')
        # attackements = request.data.get('attackements')
        attackements = []
        # ht_object = Hanhtrinh.objects.get(hanhtrinh_id=hanhtrinh)
        # ht_object.odo_start= km_end
        # ht_object.save()
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company

        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        vantai.capnhatsokmbatdauhanhtrinh(hanhtrinh, km_end, None, attackements)
            # attachments = body['attachments']
            # for item in attachments:
            #     atts= AttackmentHanhTrinh.objects.filter(hanhtrinh = ht_object, url=item)
            #     if len(atts) == 0:
            #         att = AttackmentHanhTrinh(hanhtrinh = ht_object, url= item)
            #         att.save()
        result = chitiethanhtrinh(hanhtrinh)
        # result['data']['sid'] = result['data']['id']
        # result['data']['id'] = ht_object.pk
        return Response(result)
class DanhsachMathang(APIView): 
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs): 
        queryset= tatcamathang()
        
        return Response(queryset)
        
class Danhsachtatcaxe(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        queryset= danhsachtatcaxe()
        print(queryset['data']['results'])
        # for item in queryset['data']['results']:
        #     hahai_id = item['id']
        #     owner_user_id = item['owner_user_id']['id']
        #     owner_user_name = item['owner_user_id']['name']
        #     license_plate = item['license_plate']
        #     name = item['name']
        #     object_xes = VantaihahaiEquipment.objects.filter(hahai_id=hahai_id)
        #     if len(object_xes) == 0:
        #         object_xe = VantaihahaiEquipment()
        #     else:
        #         object_xe = object_xes[0]
        #     object_xe.hahai_id = hahai_id
        #     object_xe.owner_user_id = owner_user_id
        #     object_xe.owner_user_name = owner_user_name
        #     object_xe.license_plate = license_plate
        #     object_xe.name = name
        #     object_xe.save()
        #     # item['sid'] = item['id']
        #     # item['id'] = object_xe.pk

        #     # print("Thông tin tai xe: ", owner_user_id)
        #     # thongtintaixe =  GetThongtintaixe(owner_user_id)
        #     # print(thongtintaixe)
        #     # members = VantaihahaiMember.objects.filter(member_id=owner_user_id)
        #     # if len(members)>0:
        #     #     member = members[0]
        #     #     member.name = thongtintaixe['data']['name']
        #     #     if thongtintaixe['data']['employee_id']:
        #     #         member.employee_id = thongtintaixe['data']['employee_id']['id']
        #     #         member.mobile_phone = thongtintaixe['data']['employee_id']['mobile_phone']
        #     #     member.save()
        #     # else:
        #     #     print("Create new member", thongtintaixe)
        #     #     if thongtintaixe['data']['employee_id']:
        #     #         member = VantaihahaiMember(member_id = owner_user_id, name = thongtintaixe['data']['name'],
        #     #                                 employee_id = thongtintaixe['data']['employee_id']['id'],
        #     #                                 mobile_phone = thongtintaixe['data']['employee_id']['mobile_phone'],
        #     #                                 updated_time = timezone.now())
        #     #         member.save()
        
        return Response(queryset)
    
class Thongtinxe(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        equitment_id = kwargs.get('equitment')
        # ht_object = VantaihahaiEquipment.objects.get(hahai_id=equitment_id)
        # user = request.user 
        try:
            # device = user.user_device
        # if device:
            
            result = thongtinxe(equitment_id)
            # result['data']['sid'] = result['data']['id']
            # result['data']['id'] = ht_object.pk
            return Response(result)
        except Exception as ex:
            print(ex)
            return Response({
                            'status': False, 
                            'error' : "You does not own any device, please create a new one"
                        })

class ListYeucaubaotrixe(APIView): 
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        equitment_id = request.data.get('equitment')
        equitment_id = kwargs.get('equitment')
        device = self.request.user.user_device
        results = []
        user_owner = device.user_owner
        if user_owner:
            device = user_owner.user_device
        company_info = device.company
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.danhsachyeucaubaotrixe(equitment_id)
        return Response(result)
        # except Exception as ex:
        #     print(ex)
        #     return Response({
        #                     'status': False, 
        #                     'error' : "You does not own any device, please create a new one"
        #                 })

class TaoghichuBaotri(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def post(self, request, *args, **kwargs): 
        equitment = kwargs.get('equitment')
        note = request.data.get('note')
        # user = request.user 
        try:
            # device = user.user_device
        # if device:
            body = request.data
            result = capnhatghichubaotri(equitment, note, body)
            return Response(result)
        except Exception as ex:
            print(ex)
            return Response({
                            'status': False, 
                            'error' : ex.message
                        })



class Danhsachcactinh(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        
        # user = request.user 
        try:
            # device = user.user_device
        # if device:
            
            result = danhsachcactinh()
            return Response(result)
        except Exception as ex:
            # print(ex)
            return Response({
                            'status': False, 
                            'error' : ex.message
                        })


class ListHuyentheotinh(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        province_id = kwargs.get('province')
        user = request.user 
        try:
            device = user.user_device
        # if device:
            
            result = danhsachcachuyentheotinh(province_id)
            return Response(result)
        except Exception as ex:
            print(ex)
            return Response({
                            'status': False, 
                            'error' : "You does not own any device, please create a new one"
                        })

class ListPhuongtheohuyen(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        district_id = kwargs.get('district')
        user = request.user 
        try:
            # device = user.user_device
        # if device:
            
            result = danhsachcacphuongtheohuyen(district_id)
            return JsonResponse(result)
        except Exception as ex:
            print(ex)
            return Response({
                            'status': False, 
                            'error' : "You does not own any device, please create a new one"
                        })


class TatcaDiadiem(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, *args, **kwargs): 
        
        # user = request.user 
        try:
            # device = user.user_device
        # if device:
            
            result = tatcadiadiem()
            return Response(result)
        except Exception as ex:
            # print(ex)
            return Response({
                            'status': False, 
                            'error' : ex.message
                        })

class Taohanhtrinh(APIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [authentication.SessionAuthentication]
    def post(self, request, *args, **kwargs): 
        # equitment = kwargs.get('equitment')
        user = request.user 
        print(user)
        is_superuser = user.is_superuser
        # admin_boad = AdminBoard.objects.filter(user=user).first()
        # if not is_superuser and  not admin_boad :
        #     return HttpResponseRedirect('/auth')
        # if is_superuser or admin_boad.is_vantaihahai_admin :
        user_devices = Device.objects.filter(user = user)
        hahai_member = None
        xe_phutrach = None
        if  len(user_devices)>0:
            print('ha hai member: ', hahai_member)
            user_device = user_devices[0]
            # device = devices[0]
            if user_device.user_owner:
                owner_devices = Device.objects.filter(user=user_device.user_owner)
                if len(owner_devices)>0:
                    user_device = owner_devices[0]
            print("tim kiem xe cua : ",hahai_member.member_id)
      
        body = {
                # "equipment_id": request.data.get('equipment_id'),
                "schedule_date": request.data.get('schedule_date'),
                "location_id": request.data.get('location_id'),
                "location_dest_id": request.data.get('location_dest_id'),
                "equipment_id":xe_phutrach.hahai_id,
                "fleet_product_id": request.data.get('fleet_product_id'),
                "employee_id":hahai_member.employee_id,
            }
        username = device.username
        password = device.password
        vantai = VanTaiHaHai(url=company_info.url, 
                    dbname= company_info.dbname,
                    username= username, 
                    password= password)
        result = vantai.themmoichuyendi(body)
        return Response(result)
        # except Exception as ex:
        #     print(ex)
        #     return Response({
        #                     'status': False, 
        #                     'error' : ex.message
        #                 })