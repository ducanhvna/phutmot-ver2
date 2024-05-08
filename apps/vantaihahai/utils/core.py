
from django.conf import  settings
import requests, json
# from .models import VantaihahaiMember, VantaihahaiMembership
import xmlrpc.client
import datetime

def chitiethanhtrinh(hanhtrinh):
     # user = order.user
    url = f'https://vantaihahai.com/api/fleet.trip/{hanhtrinh}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Chi tiet hanh trinh: ", hanhtrinh)
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None

class VanTaiHaHai():
    def __init__(self,url=None, dbname= None, username=None, password=None):
        print('init hahai')
        try:
            self.url = url if url else settings.VANTAIHAHAI_CONFIG['url']
            self.db = dbname if dbname else settings.VANTAIHAHAI_CONFIG['db'] 
            self.username = username if username else settings.VANTAIHAHAI_CONFIG['username']
            self.password = password if password else settings.VANTAIHAHAI_CONFIG['password']
            self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            self.uid = common.authenticate(self.db, self.username, self.password, {})
        except Exception as ex:
            print("day la: ", ex)
    def getlistemployee(self):
        domain = ['&',('active', '=', True), ('user_id', '=', self.uid)]
        employees = self.models.execute_kw(self.db, self.uid,  self.password, 'hr.employee', 'search_read', [domain], 
        {'fields': ['id', 'name', 'user_id',
                        'company_id']})
        return employees
   
    def tatcachuyendicuataixe(self, employee_id=None):
        if not employee_id:

            employees = self.getlistemployee()
            # employee_code = employees[0]['code']
            employee_id = employees[0]['id']
            
        results = []
        if employee_id>0:
            results = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'search_read', 
                [[('employee_id','=', employee_id)]], {'fields': ['id', 'company_id', "currency_id", "equipment_id", "location_name",
                        "location_dest_name", "location_id", "location_dest_id", 'eating_fee', 'note', 'odometer_start', 'odometer_dest',
                        'odometer_end', 'employee_id', 'schedule_date', 'start_date', 'end_date', 'attachment_ids', 'fleet_product_id',]})
            for item in results:
                item['fleet_product_id'] = {'id': item['fleet_product_id'][0], 'name': item['fleet_product_id'][1]} \
                        if item['fleet_product_id'] else None
                item['company_id'] ={'id':  item['company_id'][0] , 'name':item['company_id'][1]} \
                                    if item['company_id'] else None
                item['location_id'] ={'id':  item['location_id'][0], 'name':item['location_id'][1]} \
                                        if item['location_id'] else None
                item['location_dest_id'] ={'id':  item['location_dest_id'][0], 'name':item['location_dest_id'][1]} \
                                        if item['location_dest_id'] else None
                item['equipment_id'] = {'id': item['equipment_id'][0], 'name':item['equipment_id'][1]} \
                                        if item['equipment_id'] else None
                item['location_name'] = item['location_name'] if item['location_name'] else None
                item['schedule_date'] = item['schedule_date'] if item['schedule_date'] else None
                item['location_dest_name'] = item['location_dest_name'] if item['location_dest_name'] else None
        return {'data':{'results': results}, 'employee': {'id': employee_id}}
    
    def tatcachuyendihomnay(self):
        today_str = datetime.datetime.now().strftime('%Y-%m-%d') 
        last_week_str = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d') 
        results = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'search_read', 
                [[('schedule_date','<=', today_str), ('schedule_date','>=', last_week_str)]], {'fields': ['id', 'company_id', "currency_id", "equipment_id", "location_name",
                        "location_dest_name", "location_id", "location_dest_id", 'eating_fee', 'note', 'odometer_start', 'odometer_dest',
                        'fleet_product_id',
                        'odometer_end', 'employee_id', 'schedule_date', 'start_date', 'end_date', 'attachment_ids']})
        for item in results:
            item['fleet_product_id'] = {'id': item['fleet_product_id'][0], 'name': item['fleet_product_id'][1]} \
                        if item['fleet_product_id'] else None
            item['company_id'] ={'id':  item['company_id'][0] , 'name':item['company_id'][1]} \
                                    if item['company_id'] else None
            item['location_id'] ={'id':  item['location_id'][0], 'name':item['location_id'][1]} \
                                    if item['location_id'] else None
            item['location_dest_id'] ={'id':  item['location_dest_id'][0], 'name':item['location_dest_id'][1]} \
                                    if item['location_dest_id'] else None
            item['equipment_id'] = {'id': item['equipment_id'][0], 'name':item['equipment_id'][1]} \
                                    if item['equipment_id'] else None
            item['location_name'] = item['location_name'] if item['location_name'] else None
            item['schedule_date'] = item['schedule_date'] if item['schedule_date'] else None
            item['location_dest_name'] = item['location_dest_name'] if item['location_dest_name'] else None
            
            
        return {'data':{'results': results,'today':today_str}}
        
    def danhsachtatcaxe(self):
        result = self.models.execute_kw(self.db, self.uid, self.password, 'maintenance.equipment', 'search_read', 
                [[]], {'fields': ['id', 'name', "owner_user_id", "last_request", "license_plate", 
                        "trip_count", "note", "message_ids"]})
        for item in result:
            try:
                item['owner_user_id'] = {'name':item['owner_user_id'][1], 'id':item['owner_user_id'][0]}
            except:
                print('item: ', item)
        return result
    def create_free_user(self, code):
        user_id= self.models.execute_kw(self.db, self.uid, self.password, 'res.users', 'create', [{'name':f"free{code}", 'login':f'free_{code}@free.com',
                'company_ids':[2], 'company_id':2, 'new_password':code}])
        
        return user_id

    def create_fist_car(self, member):
        update_data = {'name': member.name, "owner_user_id":member.member_id, "license_plate": member.name}
        car_id= self.models.execute_kw(self.db, self.uid, self.password, 'maintenance.equipment', 'create', [update_data])
        return car_id
    def create_employee(self, code, member_id):
        update_data = {
                'user_id': member_id,
                'name': code,
                'company_id': 2
            }
        id_employee = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'create',
                                                  [update_data])
        return id_employee
    def chitietxe(self, xe_id):
     # user = order.user
        [result] = self.models.execute_kw(self.db, self.uid, self.password, 'maintenance.equipment', 'read',
                [xe_id],{'fields':['id', 'name', "owner_user_id", "last_request", "license_plate",
                        "trip_count", "note", "message_ids"]})
        try:
            result['owner_user_id'] = {'name':result['owner_user_id'][1], 'id':result['owner_user_id'][0]}
        except:
            print('item: ', result)
        print(result)
        return result
    def themmoichuyendi(self, body, drive_user, drive_pass):
        print("Bat dau them moi chuyen di")
        # Get list chuyen di
       
        location_ids = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.location',  'search', [[]], {})
        list_locations = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.location', 'read',
                [location_ids],{'fields':['id','ward_id', 'district_id','state_id']})
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        drive_uid = common.authenticate(self.db, drive_user, drive_pass, {})
        employee_ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'search',[[('user_id','=',drive_uid)],{}])
        if len(employee_ids)>0:
            body['employee_id'] = employee_ids[0]
        else:
            body['employee_id'] = False
        print("danh sach dia chir", list_locations)
      
        location_id = body['location_id']
        location_dest_id = body['location_dest_id']
        location_start = None
        location_dest = None
        for location in list_locations:
            try:
                if location['id'] == int(location_id):
                    print('tim thay: bat dau', location_id)
                    location_start = location
                if location['id'] == int(location_dest_id):
                    print('tim thay: kt', location_id)
                    location_dest = location
            except Exception as ex:
                print("except tao xe", ex)
        if location_start != None:
            try:
                body['ward_id'] = location_start['ward_id'][0]
                body['district_id'] = location_start['district_id'][0]
                body['state_id'] = location_start['state_id'][0]
            except Exception as ex:
                print('start errr', ex)
        if location_dest != None:
            try:
                body['ward_dest_id'] = location_dest['ward_id'][0]
                body['district_dest_id'] = location_dest['district_id'][0]
                body['state_dest_id'] = location_dest['state_id'][0]
            except Exception as ex:
                print('des errr', ex)
        print('chot ha: ', body)
        for k in body.keys():
            if not body[k]:
                body[k] = False
        id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'create', [body])
        [result] = results = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read', [[id_trip]],
                 {'fields': ['id', 'company_id', "currency_id", "equipment_id", "location_name",
                        "location_dest_name", "location_id", "location_dest_id", 'eating_fee', 'note', 'odometer_start', 'odometer_dest',
                        'odometer_end', 'employee_id', 'schedule_date', 'start_date', 'end_date', 'attachment_ids', 'fleet_product_id']})
        return {'data': result}
    def capnhatsokmketthuchanhtrinh(self, hanhtrinh, sokm, body, attackements=None):
        result = None
        try:
            fleet_trip_object = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read',
                    [[hanhtrinh]],{'fields':['id','equipment_id', 'odometer_start','odometer_dest', 'odometer_end']})
            print('cap nhat file dinh kem')
            
            try:
                # url = url + '&attachments={}'.format(attackements)
                for attachment in attackements :
                    try:
                        if attachment:
                            id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'ir.attachment', 'create', [{
                                'name': fleet_trip_object[0]['equipment_id'][1],
                                'type': 'url',
                                'url': attachment,
                                'res_model': 'fleet.trip',
                                'res_id': hanhtrinh, }])
                    except Exception as ex:
                        print(ex)
            except Exception as ex:
                print(ex)
        except Exception as ex:
                print(ex)
        try:
            print("Cap nhat so km ket thuc ")
            # km_start =  fleet_trip_object['odometer_start'] if fleet_trip_object['odometer_start'] else 0
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {"odometer_dest": sokm}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            # result['hanhtrinh'] = hanhtrinh
            result = {'data': result[0]}
            # print('result: ', result)
        except Exception as ex:
            if hasattr(ex, 'message'):
                message  = ex.message
            else:
                message = f'{ex}'
            result = {'data': None, 'error': message, 'km': sokm, 'id': hanhtrinh}
        return result
    def capnhatsokmbatdauhanhtrinh(self, hanhtrinh, sokm, body, attackements=None):
        result = None
        try:
            fleet_trip_object = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read',
                    [[hanhtrinh]],{'fields':['id','equipment_id', 'odometer_start','odometer_dest']})
            print('cap nhat file dinh kem')
            try:
                # url = url + '&attachments={}'.format(attackements)
                for attachment in attackements:
                    id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'ir.attachment', 'create', [{
                            'name': fleet_trip_object[0]['equipment_id'][1],
                            'type': 'url',
                            'url': attachment,
                            'res_model': 'fleet.trip',
                            'res_id': hanhtrinh,
                        }])
            except Exception as ex:
                print(ex)
        except Exception as ex:
            print(ex)
            
        try:
            print("Cap nhat so km ket thuc ")
        
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'odometer_start': sokm}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            print(ex)
        return result

    def capnhathanghoa(self, hanhtrinh, fleet_product_id):
        result = None
        try:
            fleet_trip_object = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read',
                    [[hanhtrinh]],{'fields':['id','equipment_id', 'fleet_product_id']})
        except Exception as ex:
            print(ex)
            
        try:
            print("Cap nhat so km ket thuc ")
        
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'fleet_product_id': fleet_product_id}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            if hasattr(ex, 'message'):
                message  = ex.message
            else:
                message = f'{ex}'
            result = {'data': None, 'error': message, 'product': fleet_product_id, 'id': hanhtrinh}
        return result

    def capnhatlocationbatdauhanhtrinh(self, hanhtrinh, location_id):
        result = None
        try:
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'location_id': location_id}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            if hasattr(ex, 'message'):
                message  = ex.message
            else:
                message = f'{ex}'
            result = {'data': None, 'error': message, 'loc': location_id, 'id': hanhtrinh}
        return result
    def capnhatlocationketthuchanhtrinh(self, hanhtrinh, location_id):
        result = None
        try:
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'location_dest_id': location_id}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            if hasattr(ex, 'message'):
                message  = ex.message
            else:
                message = f'{ex}'
            result = {'data': None, 'error': message, 'loc': location_id, 'id': hanhtrinh}
        return result
    
    def danhsachyeucaubaotrixe(self, equimentid):
    # user = order.user

        result = self.models.execute_kw(self.db, self.uid, self.password, 'maintenance.request', 'search_read', 
                [[('equipment_id','=', equimentid)]], {'fields': ['id', 'equipment_id', "category_id", "request_date", "maintenance_type", 
                        "description", "odometer_maintenance"]})
        for item in result:
            item['equipment_id'] = None if item['equipment_id'] == False else {'id': item['equipment_id'][0], 'name':  item['equipment_id'][1]}
            item['category_id'] = None if item['category_id'] == False else {'id': item['category_id'][0], 'name': item['category_id'][1]}
            item['request_date'] = None if item['request_date'] == False else item['request_date']
            item['maintenance_type'] = None if item['maintenance_type'] == False else item['maintenance_type']
            item['odometer_maintenance'] = None if item['odometer_maintenance'] == False else item['odometer_maintenance']
            item['description'] = None if item['description'] == False else item['description']
        return {'data': {'results': result}}
        
    
def checkishasmembership(device):
    result = VantaihahaiMembership.objects.filter(device=device)
    return len(result)>0

def CreateVantaihahaiMember(device, member_id, name):
    new_memmber = VantaihahaiMember(member_id= member_id, name = name)
    new_memmber.save()

    vt_m_object = VantaihahaiMembership(device = device, member= new_memmber)
    vt_m_object.save()

    return vt_m_object


def CreatenewUser(username,password):
    url = f'https://vantaihahai.com/api/res.users'
    register_token = settings.VANTAIHAHAI_CONFIG['register_token']
    headers = {
        # 'Content-Type': 'application/json',
        # 'access_token': f'{access_token}'
    }

    print("Tao user moi ")
    data = {
            "register_token": register_token,
            "name": username,
            "email": f"{username}@vantaihahai.com",
            "password": password
        }
    response = requests.request("POST", url,  data=json.dumps(data))
    print(response)
    
    if response.status_code == 201:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None

def GetToken(username,password):
    # user = order.user
    username = f'{username}@vantaihahai.com'
    url = f'https://vantaihahai.com/api/auth/get_tokens?username={username}&password={password}&access_lifetime=72000&refresh_lifetime=72000'
    # access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    # headers = {
    #     # 'Content-Type': 'application/json',
    #     'access_token': f'{access_token}'
    # }

    print("Lay thong tin tai xe: ")
   
    response = requests.request("GET", url)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None

def GetThongtintaixe(driver_id):
    
    # user = order.user
    url = f'https://vantaihahai.com/api/res.users/{driver_id}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Lay thong tin tai xe: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None

def tatcachuyendicuataixe(emmployeeid = None):
    try:
        # user = order.user
        if emmployeeid:
            url = f'https://vantaihahai.com/api/fleet.trip?employee_id={emmployeeid}'
        else:
            url = 'https://vantaihahai.com/api/fleet.trip'
        access_token = settings.VANTAIHAHAI_CONFIG['access_token']
        headers = {
            # 'Content-Type': 'application/json',
            'access_token': f'{access_token}'
        }

        print("Lay tatca chuyen tai xe: ")
    
        response = requests.request("GET", url, headers=headers)
        print(response)
        
        if response.status_code == 200:
            # order.haravan_order = response_json['order']['name']
            # order.save() 
            response_json =  response.json()
            return response_json
        else:
            return {'data':{'results':[]}}
    except Exception as ex:
        return {'data':{'results':[]}}

def cacchuyendihomnaycuataixe(emmployeeid):
    # user = order.user
    url = f'https://vantaihahai.com/api/fleet.trip?date=today&employee_id={emmployeeid}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Cac chuyen di hom nay: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None



def danhsachtatcaxe():
    # user = order.user
    url = f'https://vantaihahai.com/api/maintenance.equipment'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Dan sach tat ca xe: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None



def thongtinxe(equimentid):
    # user = order.user
    url = f'https://vantaihahai.com/api/maintenance.equipment/{equimentid}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Get Thong tin xe: ", equimentid)
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None



def danhsachyeucaubaotrixe(equimentid):
    # user = order.user
    url = f'https://vantaihahai.com/api/maintenance.request?equipment_id={equimentid}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Danh sach yeu cau bao tri xe: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None




def danhsachcactinh():
    # user = order.user
    url = f'https://vantaihahai.com/api/province'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Dan sach cac tinh: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None


def danhsachcachuyentheotinh(stateid):
    # user = order.user
    url = f'https://vantaihahai.com/api/district?state_id={stateid}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Danh sach huyen theo tinh: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None


def danhsachcacphuongtheohuyen(district_id):
    # user = order.user
    url = f'https://vantaihahai.com/api/ward?district_id={district_id}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Danh sach yeu cau bao tri xe: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None


def capnhatsokmbatdauhanhtrinh(hanhtrinh, sokm, body, attackements=None):
    # user = order.user
    url = f'https://vantaihahai.com/api/fleet.trip/{hanhtrinh}/do_odometer_start?odometer_start={sokm}'
    if attackements:
        url = url + '&attachments={}'.format(attackements)
    print("call: ",url)
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Cap nhat so km bat dau ")
   
    response = requests.request("PUT", url, headers=headers, data=json.dumps(body))
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None

def capnhatsokmketthuchanhtrinh(hanhtrinh, sokm, body, attackements=None):
    # user = order.user
    print('update: ',hanhtrinh)
    url = f'https://vantaihahai.com/api/fleet.trip/{hanhtrinh}/do_odometer_end?odometer_end={sokm}'
    if attackements:
        url = url + '&attachments={}'.format(attackements)
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Cap nhat so km ket thuc ")
   
    response = requests.request("PUT", url, headers=headers, data=json.dumps(body))
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None



def capnhatghichubaotri(equitment, ghichu, body):
    # user = order.user
    url = f'https://vantaihahai.com/api/maintenance.equipment/{equitment}/create_maintenance_request?note={ghichu}'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print(f"Cap nhat ghi chu: {ghichu} cho xe: {equitment}")
   
    response = requests.request("PUT", url, headers=headers, data=json.dumps(body))
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None


def themmoichuyendi(body):
    # user = order.user
    url = f'https://vantaihahai.com/api/fleet.trip'
   
    print("Them moi chuyen di")
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    response = requests.request("POST", url,headers=headers, data=json.dumps(body))
    print(response)
    print(response.json())
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None



def danhsachmathang():
    # user = order.user
    url = f'https://vantaihahai.com/api/fleet.product'
    access_token = settings.VANTAIHAHAI_CONFIG['access_token']
    headers = {
        # 'Content-Type': 'application/json',
        'access_token': f'{access_token}'
    }

    print("Dan sach cac mat hang: ")
   
    response = requests.request("GET", url, headers=headers)
    print(response)
    
    if response.status_code == 200:
        # order.haravan_order = response_json['order']['name']
        # order.save() 
        response_json =  response.json()
        return response_json
    else:
        return None


def tatcadiadiem():
    try:
       
        url = 'https://vantaihahai.com/api/fleet.location'
        access_token = settings.VANTAIHAHAI_CONFIG['access_token']
        headers = {
            # 'Content-Type': 'application/json',
            'access_token': f'{access_token}'
        }

        print("Lay tat ca dia diem cua xe: ")
    
        response = requests.request("GET", url, headers=headers)
        print(response)
        
        if response.status_code == 200:
            # order.haravan_order = response_json['order']['name']
            # order.save() 
            response_json =  response.json()
            return response_json
        else:
            return {'data':{'results':[]}}
    except Exception as ex:
        return {'data':{'results':[]}}


def tatcamathang():
    try:
       
        url = 'https://vantaihahai.com/api/fleet.product'
        access_token = settings.VANTAIHAHAI_CONFIG['access_token']
        headers = {
            # 'Content-Type': 'application/json',
            'access_token': f'{access_token}'
        }

        print("Lay tat ca dia diem cua xe: ")
    
        response = requests.request("GET", url, headers=headers)
        print(response)
        
        if response.status_code == 200:
            # order.haravan_order = response_json['order']['name']
            # order.save() 
            response_json =  response.json()
            return response_json
        else:
            return {'data':{'results':[]}}
    except Exception as ex:
        return {'data':{'results':[]}}