import sys, requests, json, os
# from dotenv import load_dotenv
import shutil
import requests
# load_dotenv()
import xmlrpc.client
import pandas as pd
import numpy as np
url = 'https://hrm.mandalahotel.com.vn'
db = 'apechrm_product_v3'
username = 'admin'
password = 'admin'
url_summary = 'https://dl.dropboxusercontent.com/scl/fi/stx1auw6wou3rnqkrjed2/Summary-time-attendant-OK.xlsx?rlkey=k2n6ayrp8r0rvk66rruzu032x'
url_attendace_count = 'https://dl.dropboxusercontent.com/scl/fi/q7dluz004pvcrcpijpetk/Ch-m-c-ng-m-s-l-n.xlsx?rlkey=zbp0nd22gcu3ipo0tczgrxnn1'
url_al_cl_tracking = 'https://dl.dropboxusercontent.com/scl/fi/3iyepiaqbwy0uoj2ogq9h/Theo-doi-ngay-phep-bu.xlsx?rlkey=i88y765pmvsns74p09r6abxt2'
url_night_split_shift = 'https://dl.dropboxusercontent.com/scl/fi/esn5favz2lr6omja6hyl9/ca-m-chi-ti-t-ca-g-y.xlsx?rlkey=8n9id7p01f7i8tnnfkkh0wp76'
url_late_5_minute = 'https://dl.dropboxusercontent.com/scl/fi/vzkt5xihgjeuenqhd1cgq/B-o-c-o-i-mu-n-d-i-5p-v-tr-n-5p.xlsx?rlkey=yhaksz20oo3zjju1hm0fk1u37'
url_feed_report = 'https://dl.dropboxusercontent.com/scl/fi/bnjpdw8nd2jsjrtowji0g/B-o-c-o-t-ng-h-p-n-ca.xlsx?rlkey=0v2ctgffrd0xgt4s73nvxdx13&dl=0'
class HrmUser():
    def __init__(self, start_date_str, end_date_str, server_url = None, server_db= None, server_username = None, server_password= None,\
                 ouput_report_folder = ''):
        super(HrmUser, self).__init__()
        if server_url:
            self.url = server_url
        else:
            self.url = url
        if server_db:
            self.db = server_db
        else:
            self.db = db
        if server_username:
            self.username = server_username
        else:
            self.username = username
        if server_password:
            self.password = server_password
        else:
            self.password = password
        self.date_array = pd.date_range(start=start_date_str, end=end_date_str)
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.user_profile = self.models.execute_kw(self.db, self.uid, self.password, 'res.users', 'read', [[self.uid] ], {'fields': ['id', 'name', 'company_id']})[0]
        self.user_id = self.user_profile['id']
        try:
            self.company_id = self.user_profile['company_id'][0]
            self.company_name = self.user_profile['company_id'][1]
            self.company_profile = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'read', [[self.company_id] ], {'fields': ['id', 'name', 'mis_id']})[0]
            self.company_mis_id = self.company_profile['mis_id']
            print(self.company_mis_id)
        except Exception as ex:
            print(ex)
            self.company_id = -1
            self.company_name = ''


        path = "unity"
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(path)
            print("The new directory is created!")

        path = "unity/template"
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)
        if not isExist:

            # Create a new directory because it does not exist
            os.makedirs(path)
            print("The new directory is created!")

        path =  'unity/template/Summary time attendant OK.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_summary, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')

        path =  'unity/template/CHAM_CONG_DEM_SO_LAN.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_attendace_count, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')

        path =  'unity/template/THEO_DOI_PHEP_BU.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_al_cl_tracking, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')

        path =  'unity/template/CA_DEM_CA_GAY.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_night_split_shift, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')

        path =  'unity/template/BAO_CAO_DI_MUON_DUOI_5P_VA_TREN_5P.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_late_5_minute, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')
        
        path =  'unity/template/BAO_CAO_TONG_HOP_AN_CA.xlsx'
        if not os.path.isfile(path):
            # url = 'https://reqbin.com/echo/get/json'
            response = requests.get(url_feed_report, stream=True)
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                print('The file was saved successfully')


        self.check_activate_employee()

    def run_update_calculate_server(self, company_id):
        # ids = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'search', [[]], {})
        list_company = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', 'read', [[company_id]], {'fields': ['id',
                                            'name', 'is_ho',
                                            'mis_id']})
        dates = pd.Series(self.date_array)
        df = pd.DataFrame(dates, columns=['dates'])
        df = df['dates'].groupby(np.arange(len(df['dates']))//32).agg(['first', 'last'])
        # for company in list_company:   
        #     if (company['id'] != company_id):
        #         continue
        #     department_ids = self.models.execute_kw(
        #         self.db, self.uid, self.password, 'hr.department', 'search', [[('company_id', '=', company['id'])]])
        #     list_departments = self.models.execute_kw(self.db, self.uid, self.password, 'hr.department', 'read', [department_ids], {
        #                                             'fields': ['id', 'name', 'total_employee', 'company_id', 'member_ids', 'time_keeping_count']})
        #     limit = 300
        #     for s_index, subset in df.iterrows():
        #         print(company['name'])
        #         print(subset)
        #         for dp in list_departments:
        #             print(dp['name'])
        #             # export_sumary_attendance_report_department
        #             # leave_data = self.models.execute_kw(self.db, self.uid, self.password,'res.users', 'export_sumary_attendance_report_department',[self.uid],
        #             #                 {'company_name': company['name'], 
        #             #                  'department_name': dp["name"],
        #             #                 'month':1, 'year':2024})
        #             # print(leave_data)
        #         try:
        #             leave_data = self.models.execute_kw(self.db, self.uid, self.password,'res.users', 'update_summary_report',[self.uid],
        #                             {'company_name': company['name'], 
        #                             'employee_code': '',
        #                             'is_update_contract': True,
        #                             'start_str': subset['first'].strftime('%Y-%m-%d'), 
        #                             'end_str':subset['last'].strftime('%Y-%m-%d'), 'page_size':limit, 'page_number':0})
        #             print("leave_data=",leave_data)
                 
        #             index = 1
        #             while (leave_data['total_records']== limit):
        #                 leave_data = self.models.execute_kw(self.db, self.uid, self.password,'res.users', 'update_summary_report',[self.uid],
        #                             {'company_name': company['name'], 
        #                             'employee_code': '',
        #                             'is_update_contract': True,
        #                             'start_str': subset['first'].strftime('%Y-%m-%d'), 
        #                             'end_str':subset['last'].strftime('%Y-%m-%d'), 'page_size':limit, 'page_number':index})
        #                 index = index+1
        #                 print("leave_data=",leave_data)
        #             # call update_shift_base_info to update_shift_result
        #             # limit = 100
        #             # update_shift_result = self.models.execute_kw(self.db, self.uid, self.password,'res.users', 'update_shift_base_info',[self.uid],
        #             #                 {'company_id': company['id'], 
        #             #                 # 'department':dp['name'],
        #             #                 'is_update_contract': False,
        #             #                 'is_compute_worktime': False,
        #             #                 'employee_code': '',
        #             #                 'start_str': subset['first'].strftime('%Y-%m-%d'), 
        #             #                 'end_str':subset['last'].strftime('%Y-%m-%d'), 'page_size':limit, 'page_number':0})
        #             # index = 1
        #             # while (update_shift_result['total_records']== limit):
        #             #     update_shift_result = self.models.execute_kw(self.db, self.uid, self.password,'res.users', 'update_shift_base_info',[self.uid],
        #             #                 {'company_id': company['id'], 
        #             #                 'is_update_contract': False,
        #             #                 'is_compute_worktime': False,
        #             #                 # 'department':dp['name'],
        #             #                 'employee_code': '',
        #             #                 'start_str': subset['first'].strftime('%Y-%m-%d'), 
        #             #                 'end_str':subset['last'].strftime('%Y-%m-%d'), 'page_size':limit, 'page_number':index})
        #             #     index = index+1
        #             # print("leave_data=",leave_data)
        #             # print('update_shift_result: ', update_shift_result)
        #             print('convert_off_to: ', leave_data['convert_off_to'])
        #             print("update company ", company['name'])
        #             print('convert_off_to: ', leave_data['traceback'])
                    
        #         except Exception as ex:
        #             print("update company ex", company['name'])
        #             # print(leave_data['traceback'])
        #             print(ex)
                    
    def check_activate_employee(self):
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'search', [["&",
                        ('company_id', '=',self.company_id),
                        ('user_id','=', self.user_id),
                        ("active", "=", False)]], {})
        print('IDS ACTIVE: ',ids)
        if len(ids)>0:
            try:
                self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'write', [ids, {'active': True}])
            except Exception as ex:
                print(ex)
    
    def rename_item(self):
        ids = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'search', 
                [[('company', '=','Công ty Cổ phần Quản lý vận hành BĐS Mandala')]], {})
        update_data = {'company': 'Công ty Cổ phần Quản lý Vận hành BĐS Mandala'}
        id_scheduling = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'write', [ids, update_data])

        print('success', len(ids))

    def turning_attendance_report(self):
        start_str = self.date_array[0].strftime('%Y-%m-%d')
        end_str = self.date_array[len(self.date_array)-1].strftime('%Y-%m-%d')
        list_scheduling_ver = self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'search_read', [["&", "&", "&",
                                                                                                                ("total_shift_work_time", '>', 0),
                                                                                                                ("date", ">=", start_str),
                                                                                                                ("date", "<=", end_str) ,"|",
                                                                                                               ('amount_cl_reserve', '>', 0),
                                                                                                               ("amount_al_reserve", ">", 0)

                                                                                                               ]], {'fields': ['id','company', 'employee_code', 'date', 'amount_al_reserve',
                                                                                                                                'missing_checkin_break', 'amount_cl_reserve', 'shift_name',
                                                                                                                                'actual_total_work_time', 'total_shift_work_time', 'total_work_time']})
        list_dat_update = []
        ids_update = {}
        for item in list_scheduling_ver:
            total_shift_work_time = item['total_shift_work_time']*60
            if ("/OFF" in item['shift_name']) or (("OFF/" in item['shift_name'])):
                total_shift_work_time = min(total_shift_work_time, 240)
            total_work_time = item['total_work_time']
            if (item['missing_checkin_break']== True):
                total_work_time = min(total_work_time, 240)
            if item['actual_total_work_time'] != min(total_shift_work_time, total_work_time + item['amount_cl_reserve'] + item['amount_al_reserve']):
                update_data = {'actual_total_work_time': min(total_shift_work_time, total_work_time + item['amount_cl_reserve'] + item['amount_al_reserve'])}
                item['update_data'] = update_data['actual_total_work_time']
                if ( update_data['actual_total_work_time'] in list_dat_update):
                    ids_update[update_data['actual_total_work_time']].append(item['id'])
                else:
                    list_dat_update.append(update_data['actual_total_work_time'])
                    ids_update[update_data['actual_total_work_time']] = [item['id']]


        
        for value in list_dat_update:
            print(f"value: {value} - ids: {ids_update[value]}")
            ids = ids_update[value]
            update_data = {'actual_total_work_time': int(value)}
            self.models.execute_kw(self.db, self.uid, self.password, 'hr.apec.attendance.report', 'write', [ids, update_data])
        try:
            df_scheduling_ver = pd.DataFrame.from_dict(list_scheduling_ver)
            df_scheduling_ver.to_excel("self_df_scheduling_ver_turn.xlsx")
        except Exception as ex:
            print("save data ex: ", ex)
        
