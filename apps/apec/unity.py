from django.conf import  settings
import requests, json
import xmlrpc.client
import datetime, calendar

def unix_time_millis(dt):
    return 0 if (dt is None) else int(dt.timestamp() * 1000000)

class Apec():
    def __init__(self, url, db, username, password):
        print('init APEC')
        try:
            self.url = url
            self.db = db
            self.username = username
            self.password = password
            self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            self.uid = common.authenticate(self.db, self.username, self.password, {})
        except Exception as ex:
            print("day la: ", ex)
            
    def getlistemployee(self):
        domain = ['&',('active', '=', True), ('user_id', '=', self.uid)]
        employees = self.models.execute_kw(self.db, self.uid,  self.password, 'hr.employee', 'search_read', [domain], 
        {'fields': ['id', 'name', 'user_id','employee_ho',
                        'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                        'probationary_contract_termination_date', 'severance_day', 'workingday',
                        'contract_ids',
                        'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level']})
        return employees

    def getattendancereport(self, date_str = None, employee_code = None):
        LIMIT_SIZE = 10
        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            
        if not employee_code:
            employees = self.getlistemployee()
            employee_code = employees[0]['code']
            
        domain = [("employee_code", '=', employee_code),
                  ("date", "=", date_str)]
        
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'search', [domain], {'offset': 0, 'limit': LIMIT_SIZE})
        list_scheduling_ver = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'read', [ids],
                                                     {'fields': ['id', 'employee_name', 'date', 'shift_name', 'employee_code', 'company','additional_company',
                                                                 'shift_start', 'shift_end', 'rest_start', 'rest_end', 'rest_shift', 'probation_completion_wage',
                                                                 'total_shift_work_time', 'total_work_time', 'time_keeping_code', 'kid_time',
                                                                 'department', 'attendance_attempt_1', 'attendance_attempt_2',
                                                                 'attendance_attempt_3', 'attendance_attempt_4', 'attendance_attempt_5',
                                                                 'attendance_attempt_6', 'attendance_attempt_7', 'attendance_attempt_8',
                                                                 'attendance_attempt_9', 'attendance_attempt_10', 'attendance_attempt_11',
                                                                 'attendance_attempt_12', 'attendance_attempt_13', 'attendance_attempt_14',
                                                                 'attendance_inout_1','attendance_inout_2','attendance_inout_3',
                                                                 'attendance_inout_4','attendance_inout_5','attendance_inout_6',
                                                                 'attendance_inout_7','attendance_inout_8','attendance_inout_9',
                                                                 'attendance_inout_10','attendance_inout_11','attendance_inout_12', 
                                                                 'attendance_inout_13','attendance_inout_14','attendance_inout_15','actual_total_work_time', 'standard_working_day',
                                                                 'attendance_attempt_15', 'last_attendance_attempt', 'night_hours_normal', 'night_hours_holiday', 'probation_wage_rate', 
                                                                 'split_shift', 'missing_checkin_break', 'leave_early', 'attendance_late', 'night_shift', 'minute_worked_day_holiday', 
                                                                 'total_attendance']})
        return list_scheduling_ver
    
    def gethrleave(self, date_str=None, employee_code = None):
        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        if not employee_code:
            employees = self.getlistemployee()
            employee_code = employees[0]['code']
        domain = [
                ("request_date_to", ">=", f'{date_str} 00:00:00'),
                ("request_date_from", "<=", f'{date_str} 23:59:59'),
                ('active', '=', True),
                ("employee_code", '=', employee_code),
                ("state", "=", "validate")
                #   ('employee_company_id', '=', self.company_id) 
                ]

        list_hr_leave = self.models.execute_kw(self.db, self.uid, self.password, 'hr.leave', 'search_read', [domain], 
            {'fields': ['id', 'employee_id', 'employee_code', 'employee_company_id', 'active',
                    'holiday_status_id', 'minutes', 'time', 'state', 'request_date_from', 'request_date_to',
                    'attendance_missing_from', 'attendance_missing_to', 'reasons', 'for_reasons',
                    'employee_company_id','multiplier_work_time', 'overtime_from', 'overtime_to']})

        return list_hr_leave
    
    def Getlistcompany(self):
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'search', [[]], {})
        list_company = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'read', [ids], {'fields': ['id',
                                            'name', 'is_ho',
                                            'mis_id']})
    def loadcalendarholiday(self):
        resource_calendar_leaves_ids = self.models.execute_kw(
            self.db, self.uid, self.password, 'resource.calendar.leaves', 'search', [[('calendar_id','=',False)]])
        resource_calendar_leaves_list = self.models.execute_kw(self.db, self.uid, self.password, 'resource.calendar.leaves', 'read', [resource_calendar_leaves_ids],
                                                               {'fields': ['id', 'name', 'company_id', 'calendar_id', 'date_from', 'date_to', 'resource_id', 'time_type']})
    
    def loadlistshift(self):
        results = []
        local_index = 0
        LIMIT_SIZE = 50
        ids = []
        while (len(ids) == LIMIT_SIZE) or (local_index == 0):
            offset = local_index * LIMIT_SIZE
            domain =[]
            ids = self.models.execute_kw(self.db, self.uid, self.password, 'shifts', 'search', [domain], {'offset': offset, 'limit': LIMIT_SIZE})
            
            list_shifts  = self.models.execute_kw(self.db, self.uid, self.password, 'shifts', 'read', [ids], {'fields': ['id', 'name', 'start_work_time',
                                                'end_work_time','total_work_time','start_rest_time','end_rest_time', 'company_id',
                                                'rest_shifts', 'fix_rest_time', 'night', 'night_eat','dinner','lunch','breakfast','efficiency_factor']}
                                                )
            for item in list_shifts:
                results.append(item)
        
                
    def getlistTask(self):
        offset = 0
        domain =domain=[('user_ids', 'in', self.uid)]
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'search', [domain], {'offset': offset})
        list_task  = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'read', [ids], {'fields': ['id', 'user_ids', 'project_id',
                                                'partner_id','date_deadline','description', 'company_id',
                                                'date_assign']}
                                                )
        unique_list = {}
        result = []
        # traverse for all elements
       
            
        for x in list_task:
            # check if exists in unique_list or not
            
            if x:
                print(x)
                if x['project_id']:
                    print(f'pass {x["project_id"]}')
                    if x['project_id'][1] not in unique_list:
                        unique_list[x['project_id'][1]] = len(result)
                        result.append({'id': x['project_id'][0], 'name': x['project_id'][1], 'tasks': [x] })
                    else:
                        result[unique_list[x['project_id'][1]]]['tasks'].append(x)
                else:
                    if 'none' not in unique_list:
                        unique_list['none'] = len(result)
                        result.append({'id': 0, 'name': 'private', 'tasks': [x] })
                    else:
                        result[unique_list['none']]['tasks'].append(x)
        for project in result:
            for item in project['tasks']:
                item['company_id'] ={'id':  item['company_id'][0] , 'name':item['company_id'][1]} \
                                        if item['company_id'] else None
                item['project_id'] ={'id':  item['project_id'][0], 'name':item['project_id'][1]} \
                                        if item['project_id'] else None
                item['partner_id'] ={'id':  item['partner_id'][0], 'name':item['partner_id'][1]} \
                                        if item['partner_id'] else None
               
        return result
    def feedfetch(self):
        offset = 0
        domain =domain=[('user_ids', 'in', self.uid)]
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'search', [domain], {'offset': offset})
        list_task  = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'read', [ids], {'fields': ['id', 'user_ids', 'project_id',
                                                'partner_id','date_deadline', 'company_id', 'create_date', 'write_date']})
        unique_list = {}
        projects = []
        results = []
        # traverse for all elements
       
            
        for x in list_task:
            # check if exists in unique_list or not
            
            if x:
                print(x)
                if x['project_id']:
                    print(f'pass {x["project_id"]}')
                    if x['project_id'][1] not in unique_list:
                        unique_list[x['project_id'][1]] = len(projects)
                        projects.append({'id': x['project_id'][0], 'name': x['project_id'][1], 'created_at': x['create_date'],'updated_at': x['write_date'],  'tasks': [x] })
                    else:
                        projects[unique_list[x['project_id'][1]]]['tasks'].append(x)
                        projects[unique_list[x['project_id'][1]]]['updated_at'] =  x['write_date']
                else:
                    if 'none' not in unique_list:
                        unique_list['none'] = len(projects)
                        projects.append({'id': 0, 'name': 'private', 'created_at': x['create_date'],'updated_at': x['write_date'], 'tasks': [x] })
                    else:
                        projects[unique_list['none']]['tasks'].append(x)
                        projects[unique_list['none']]['updated_at'] =  x['write_date']
        for project in projects:
            results.append({
                'id': project['id'],
                'user_id': self.uid,
                'desc': None,
                'comments_count' : len(project['tasks']),
                'likes_count': 0,
                'created_at': project['created_at'] ,
                'updated_at': project['updated_at'] ,
                'is_like': None,
                'content': None,
                'user': None
            })
            # for item in project['tasks']:
            #     item['company_id'] ={'id':  item['company_id'][0] , 'name':item['company_id'][1]} \
            #                             if item['company_id'] else None
            #     item['project_id'] ={'id':  item['project_id'][0], 'name':item['project_id'][1]} \
            #                             if item['project_id'] else None
            #     item['partner_id'] ={'id':  item['partner_id'][0], 'name':item['partner_id'][1]} \
            #                             if item['partner_id'] else None
               
        return results

    def addJob(self, project_id, deadline, content):
        try:
            ids = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'create', [{
                'user_ids': [self.uid], 
                'project_id': project_id, 'partner_id': False, 'date_deadline': deadline , 'company_id':False}])
            [result]  = self.models.execute_kw(self.db, self.uid, self.password, 'project.task', 'read', [ids], {'fields': ['id', 'user_ids', 'project_id',
                                                'partner_id','date_deadline', 'company_id', 'create_date', 'write_date']})
        except:
            result = None

        return result

    def fetchRoomByMonth(self, fisttime):
        last_month_fist_day_str = (fisttime - datetime.timedelta(days=2)).replace(day=1).strftime('%Y-%m-%d')
        _, lastday = calendar.monthrange(fisttime.year, fisttime.month)
        results = []
        end_str = fisttime.replace(day=lastday).strftime('%Y-%m-%d')
        domain = ['&',('active', '=', True), ('user_id','=', self.uid)]
        employee_Sids = self.models.execute_kw( self.db, self.uid,  self.password, 'hr.employee', 'search', [domain],
                                                                                                {'offset': 0, 'limit': 1})
        list_employees = self.models.execute_kw( self.db, self.uid,  self.password, 'hr.employee', 'read', [employee_Sids], {'fields': ['id', 'name', 'user_id', 'employee_ho', 'part_time_company_id', 'part_time_department_id',
                                                                                                                            'company_id', 'code', 'department_id', 'time_keeping_code', 'job_title',
                                                                                                                            'probationary_contract_termination_date', 'severance_day', 'workingday',
                                                                                                                            'probationary_salary_rate', 'resource_calendar_id', 'date_sign', 'level']})
        employee = list_employees[0]
        code = employee['code']
        
        fields = ['id', 'employee_name', 'date', 'shift_name', 'employee_code', 'company','additional_company',
                                                                 'shift_start', 'shift_end', 'rest_start', 'rest_end', 'rest_shift', 'probation_completion_wage',
                                                                 'total_shift_work_time', 'total_work_time', 'time_keeping_code', 'kid_time',
                                                                 'department', 'attendance_attempt_1', 'attendance_attempt_2', 'minutes_working_reduced', 
                                                                 'attendance_attempt_3', 'attendance_attempt_4', 'attendance_attempt_5',
                                                                 'attendance_attempt_6', 'attendance_attempt_7', 'attendance_attempt_8',
                                                                 'attendance_attempt_9', 'attendance_attempt_10', 'attendance_attempt_11',
                                                                 'attendance_attempt_12', 'attendance_attempt_13', 'attendance_attempt_14',
                                                                 'attendance_inout_1','attendance_inout_2','attendance_inout_3',
                                                                 'attendance_inout_4','attendance_inout_5','attendance_inout_6',
                                                                 'attendance_inout_7','attendance_inout_8','attendance_inout_9', 'amount_al_reserve', 'amount_cl_reserve',
                                                                 'attendance_inout_10','attendance_inout_11','attendance_inout_12', 
                                                                 'attendance_inout_13','attendance_inout_14','attendance_inout_15','actual_total_work_time', 'standard_working_day',
                                                                 'attendance_attempt_15', 'last_attendance_attempt', 'night_hours_normal', 'night_hours_holiday', 'probation_wage_rate', 
                                                                 'split_shift', 'missing_checkin_break', 'leave_early', 'attendance_late', 'night_shift', 'minute_worked_day_holiday','total_attendance',
                                                                 'ot_holiday', 'ot_normal','create_date', 'write_date']
        domain = ["&","&", ("date", ">=", fisttime),
                                    ("date", "<=", end_str), ('employee_code','=', code)]
        
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'search', [domain],  {'offset': 0})
        list_scheduling_ver = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'read', [ids],
                                                    {'fields':fields})
        for project in list_scheduling_ver:
            results.append({
                'id': project['id'],
                'user_id': self.uid,
                'desc': None,
                'title': f"{project['date']} - {project['shift_name']}",
                'interest_ids': f"{fisttime.month}",
                'comments_count' : 0,
                'likes_count': 0,
                'userRoomStatus': 5,
                'created_at': project['create_date'] ,
                'updated_at': project['write_date'] ,
                'is_like': None,
                'content': None,
                'user': None
            })               
        return results
    def fetchChatAttendance(self, attendanceId):
        ids = [attendanceId]
        fields = ['id', 'employee_name', 'date', 'shift_name', 'employee_code', 'company','additional_company',
                                                                 'shift_start', 'shift_end', 'rest_start', 'rest_end', 'rest_shift', 'probation_completion_wage',
                                                                 'total_shift_work_time', 'total_work_time', 'time_keeping_code', 'kid_time',
                                                                 'department', 'attendance_attempt_1', 'attendance_attempt_2', 'minutes_working_reduced', 
                                                                 'attendance_attempt_3', 'attendance_attempt_4', 'attendance_attempt_5',
                                                                 'attendance_attempt_6', 'attendance_attempt_7', 'attendance_attempt_8',
                                                                 'attendance_attempt_9', 'attendance_attempt_10', 'attendance_attempt_11',
                                                                 'attendance_attempt_12', 'attendance_attempt_13', 'attendance_attempt_14',
                                                                 'attendance_inout_1','attendance_inout_2','attendance_inout_3',
                                                                 'attendance_inout_4','attendance_inout_5','attendance_inout_6',
                                                                 'attendance_inout_7','attendance_inout_8','attendance_inout_9', 'amount_al_reserve', 'amount_cl_reserve',
                                                                 'attendance_inout_10','attendance_inout_11','attendance_inout_12', 
                                                                 'attendance_inout_13','attendance_inout_14','attendance_inout_15','actual_total_work_time', 'standard_working_day',
                                                                 'attendance_attempt_15', 'last_attendance_attempt', 'night_hours_normal', 'night_hours_holiday', 'probation_wage_rate', 
                                                                 'split_shift', 'missing_checkin_break', 'leave_early', 'attendance_late', 'night_shift', 'minute_worked_day_holiday','total_attendance',
                                                                 'ot_holiday', 'ot_normal','create_date', 'write_date']
        
        list_scheduling_ver = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'read', [ids],
                                                    {'fields':fields})
        results = []
        
        for item in list_scheduling_ver:
            # item['fleet_product_id'] = {'id': item['fleet_product_id'][0], 'name': item['fleet_product_id'][1]} \
            #         if item['fleet_product_id'] else None
            # item['company_id'] ={'id':  item['company_id'][0] , 'name':item['company_id'][1]} \
            #                     if item['company_id'] else None
            # item['location_id'] ={'id':  item['location_id'][0], 'name':item['location_id'][1]} \
            #                         if item['location_id'] else None
            # item['location_dest_id'] ={'id':  item['location_dest_id'][0], 'name':item['location_dest_id'][1]} \
            #                         if item['location_dest_id'] else None
            # item['equipment_id'] = {'id': item['equipment_id'][0], 'name':item['equipment_id'][1]} \
            #                         if item['equipment_id'] else None
            # item['location_name'] = item['location_name'] if item['location_name'] else None
            # item['schedule_date'] = item['schedule_date'] if item['schedule_date'] else None
            # item['location_dest_name'] = item['location_dest_name'] if item['location_dest_name'] else None
            # dt = 0
            dt = datetime.datetime.strptime(item["date"], "%Y-%m-%d")

            msg = {
                'id': f'{unix_time_millis(dt)}',
                'content': item['date'] ,
                'thumbnail': '',
                'msg':f'Ngày dự kiến: {item["date"]}',
                'msgType': "TEXT",
                'senderId': 0,
                'reply': ''
                
            }
            results.append(msg)


            dt2 = dt + datetime.timedelta(seconds=2)
            msg = {
                'id': f'{unix_time_millis(dt=dt2)}',
                'content': f"{item['shift_name']}" ,
                'thumbnail': '',
                'msg':f'odoo xuất phát - {item["shift_name"]}',
                'msgType': "TEXT",
                'senderId': 0,
                'reply': ''
                
            }

            results.append(msg)

           
        return  results
      
    def getinvalidtimesheet(self, date_str=None, employee_code = None):
        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        if not employee_code:
            employees = self.getlistemployee()
            employee_code = employees[0]['code']
        domain = [("invalid_date", "=", date_str),
                    ("employee_code", "=", employee_code)]
        
        explanation_ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.invalid.timesheet', 'search',
                                                 [domain])
        list_old_explanation = self.models.execute_kw(self.db, self.uid, self.password, 'hr.invalid.timesheet', 'read', [explanation_ids], 
                {'fields': ['id', 'employee_id', 'employee_code', 'department', 'company_id',
                'position', 'invalid_date', 'invalid_type', 'shift_from', 'shift_to',
                'shift_break', 'real_time_attendance_data',
                'validated', 'reason', 'reason', 'remarks', 'validation_data']})

        return list_old_explanation
    
    def authenticate(self, username, password):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, username, password, {})
        return uid
    def GetListCompany(self):
        result = self.models.execute_kw(self.db, self.uid, self.password, 'res.users', 'read', 
                [[self.uid]], {'fields': ['id', 'company_ids']})
        company_ids = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'name_get',
                [result[0]['company_ids']])
        return company_ids
       
    def tatcachuyendicuataixe(self, employee_id):
        results = []
        if employee_id>0:
            results = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'search_read', 
                [[('employee_id','=', employee_id)]], {'fields': ['id', 'company_id', "currency_id", "equipment_id", "location_name",
                        "location_dest_name", "location_id", "location_dest_id", 'eating_fee', 'note', 'odometer_start', 'odometer_dest',
                        'odometer_end', 'employee_id', 'schedule_date', 'start_date', 'end_date', 'attachment_ids']})
        return {'data':{'results': results}}
    
    def tatcachuyendihomnay(self):
        today_str = datetime.datetime.now().strftime('%Y-%m-%d') 
        last_week_str = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d') 
        results = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'search_read', 
                [[('schedule_date','<=', today_str), ('schedule_date','>=', last_week_str)]], {'fields': ['id', 'company_id', "currency_id", "equipment_id", "location_name",
                        "location_dest_name", "location_id", "location_dest_id", 'eating_fee', 'note', 'odometer_start', 'odometer_dest',
                        'odometer_end', 'employee_id', 'schedule_date', 'start_date', 'end_date', 'attachment_ids']})
        for item in results:
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
    def themmoichuyendi(self, body):
        print("Bat dau them moi chuyen di")
        # Get list chuyen di
       
        location_ids = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.location',  'search', [[]], {})
        list_locations = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.location', 'read',
                [location_ids],{'fields':['id','ward_id', 'district_id','state_id']})
    
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
        id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'create', [body])
       
        return id_trip
    def capnhatsokmketthuchanhtrinh(self, hanhtrinh, sokm, body, attackements=None):
        result = None
        try:
            fleet_trip_object = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read',
                    [[hanhtrinh]],{'fields':['id','equipment_id', 'odometer_start','odometer_dest']})
            print('cap nhat file dinh kem')
            if attackements:
                # url = url + '&attachments={}'.format(attackements)
                for attachment in attackements:
                    id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'ir.attachment', 'create', [{
                            'name': fleet_trip_object[0]['equipment_id'][1],
                            'type': 'url',
                            'url': attachment,
                            'res_model': 'fleet.trip',
                            'res_id': hanhtrinh,
                        }])
        
            print("Cap nhat so km ket thuc ")
        
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'odometer_dest': sokm}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            print(ex)
        return result
    def capnhatsokmbatdauhanhtrinh(self, hanhtrinh, sokm, body, attackements=None):
        result = None
        try:
            fleet_trip_object = self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'read',
                    [[hanhtrinh]],{'fields':['id','equipment_id', 'odometer_start','odometer_dest']})
            print('cap nhat file dinh kem')
            if attackements:
                # url = url + '&attachments={}'.format(attackements)
                for attachment in attackements:
                    id_trip = self.models.execute_kw(self.db, self.uid, self.password, 'ir.attachment', 'create', [{
                            'name': fleet_trip_object[0]['equipment_id'][1],
                            'type': 'url',
                            'url': attachment,
                            'res_model': 'fleet.trip',
                            'res_id': hanhtrinh,
                        }])
        
            print("Cap nhat so km ket thuc ")
        
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'odometer_start': sokm}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            print(ex)
        return result
    def capnhatlocationbatdauhanhtrinh(self, hanhtrinh, location_id):
        result = None
        try:
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'location_id': location_id}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            print(ex)
        return result
    def capnhatlocationketthuchanhtrinh(self, hanhtrinh, location_id):
        result = None
        try:
            self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'write', [[hanhtrinh], {'location_id': location_id}])
            # get record name after having changed it
            result =  self.models.execute_kw(self.db, self.uid, self.password, 'fleet.trip', 'name_get', [[hanhtrinh]])
            print('result: ', result)
        except Exception as ex:
            print(ex)
        return result
        
        