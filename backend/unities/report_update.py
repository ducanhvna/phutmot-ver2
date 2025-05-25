from django.conf import settings
from apps.home.unities.hrms_user import HrmUser
from django.utils import timezone
import os, calendar, sys, datetime, shutil
from apps.home.unities.hrms_excel_report_v2 import HrmExcelReport_v2
from apps.home.unities.hrms_excel_file import HrmExcelFile
from apps.home.unities.attendence_report import AttendenceReportModel
import json
import uuid
import pandas as pd
from django.conf import settings
from minio import Minio

LOCAL_MAC_ADDRESS = str(hex(uuid.getnode()))
print(LOCAL_MAC_ADDRESS)
SERVER_PASSWORD = settings.SERVER_PASSWORD
df_time_recorder = None
def check_server_avaiable():
    global df_time_recorder
    global SERVER_PASSWORD
    result = False
    # config_file = os.path.join (settings.CLOUD_OUTPUT_REPORT_FOLDER, 'Config.xlsx')
    config_file = 'https://dl.dropboxusercontent.com/scl/fi/tup2bwao3ososd1h7hj04/Config.xlsx?rlkey=h7syiq8iby3l545e7fdmr0doq&dl=0'
    df_config = pd.read_excel(config_file, engine='openpyxl', index_col=0) 
    config = df_config[df_config['MAC']==LOCAL_MAC_ADDRESS]
    if len(config.index)>0:
        result = config.iloc[0]['ACTIVATE']
        SERVER_PASSWORD = config.iloc[0]['SERVER_PASSWORD']
    # try:
    df_time_recorder = pd.read_excel(config_file, engine='openpyxl', sheet_name='TIME-KEEPING') 
    # except Exception as ex:
    #     print(ex)
    print(LOCAL_MAC_ADDRESS)
    return True



def update_report():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 60 seconds: Check user")
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month == 0:
        current_month = 12
    is_load_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        is_load_result = True
        al_result_create = data['create_al']
        al_result_update = data['update_al']
        cl_result_create = data['create_cl']
        cl_result_update = data['update_cl']
    except:
        is_load_result = False
        al_result_create = {}
        al_result_update = {}
        cl_result_create = {}
        cl_result_update = {}

    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'

    user_model = HrmUser(startdate, enddate, 
        server_url = settings.SERVER_URL, server_db = settings.SERVER_URL_DB, 
        server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD)
    # user_model.turning_attendance_report()
    # if (today.minute % 3 == 0):
    print('company_id = ', today.minute)
    user_model.run_update_calculate_server(company_id=today.minute)

def post_inspection():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    print("this function runs every 12000 seconds: Load File")
    today = timezone.now()
    select_current_year = today.year - 1 if (today.month <= 2) else today.year
    select_current_month = today.month- 2 
    if select_current_month <= 0:
        select_current_month = select_current_month + 12
    
    print(f"{select_current_year}, {select_current_month}")
    date_range = calendar.monthrange(select_current_year,select_current_month)
    startdate = f'{"{:02d}".format(select_current_month)}/01/{select_current_year}'
    enddate = f'{"{:02d}".format(select_current_month)}/{"{:02d}".format(date_range[1])}/{select_current_year}'
    is_update_scheduling = True
    is_update_al_cl = False
    output_reportfolder_path = f'{select_current_month}-{today.minute}'
    isExist = os.path.exists(output_reportfolder_path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(output_reportfolder_path)
        print("The new output_report_folder is created! ", output_reportfolder_path)
    model = HrmExcelReport_v2(server_username= settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, \
        server_url=settings.SERVER_URL, \
        server_db=settings.SERVER_URL_DB, \
        start_date_str=startdate, end_date_str=enddate, ouput_report_folder= output_reportfolder_path, is_update_al_cl=is_update_al_cl, \
        is_load_df_old = False)
    model.export_data_to_files()
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate,
                server_db= settings.SERVER_URL_DB,\
                server_url=settings.SERVER_URL,
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD,
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, is_post_inspection=True, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url)
    try:
        if (today.minute % 2) == 0:
            file_model.export_sumary_attendance_report_ho()
    except Exception as ex:
        print(" file_model.export_sumary_attendance_report ho", ex)
    try:
        file_model.export_sumary_attendance_report()
    except Exception as ex:
        print(" file_model.export_sumary_attendance_report()", ex)
    # try:
    #     file_model.export_al_cl_report()
    # except Exception as ex:
    #     print(" file_model.export_al_cl_report()", ex)
    # try:
    #     file_model.export_night_shift_report()
    # except Exception as ex:
    #     print(" file_model.export_night_shift_report()", ex)
    # try:
    #     file_model.export_late_in_5_miniutes_report()
    # except Exception as ex:
    #     print('export_late_in_5_miniutes_report', ex)
    # try:
    #     file_model.export_feed_report()
    # except Exception as ex:
    #     print('export_feed_report', ex)

    # try:
    #     file_model.export_attendence_scheduling_report()
    # except Exception as ex:
    #     print('export_attendence_scheduling_report', ex)
   
    # CLOUD_OUTPUT_REPORT_FOLDER = /Users/dungbui299/Dropbox/APECHRMS/OutputReport
def export_report_ho_next_month():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year + 1 if ((today.day >= 15) and (today.month == 12)) else today.year
    current_month = today.month + 1 if today.day >= 15 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    if current_month >= 13:
        current_month = current_month - 12

    print("this function runs every 427 seconds: Export data HO")
    is_load_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        output_reportfolder_path = (data['folder_path'])
        report_folder_basename = os.path.basename(output_reportfolder_path)
        if (current_month != int(report_folder_basename.split('-')[0].strip())):
            print(f"{current_month} != {int(report_folder_basename.split('-')[0].strip())}") 
            return
        is_load_result = True
        al_result_create = data['create_al']
        al_result_update = data['update_al']
        cl_result_create = data['create_cl']
        cl_result_update = data['update_cl']
    except Exception as ex:
        print(ex)
        is_load_result = False
        al_result_create = {}
        al_result_update = {}
        cl_result_create = {}
        cl_result_update = {}

    is_load_df_old = (today.minute<32) and (today.minute>5)
    
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = True if current_month == today.month else False
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url=settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)
    file_model.export_sumary_attendance_report_ver2()
    file_model.export_al_cl_report_ho()
    file_model.export_kpi_weekly_report_ho()
    file_model.export_sumary_attendance_report_ho()


def export_report_ho():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 427 seconds: Export data HO")
    is_load_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        output_reportfolder_path = (data['folder_path'])
        report_folder_basename = os.path.basename(output_reportfolder_path)
        if (current_month != int(report_folder_basename.split('-')[0].strip())):
            print(f"{current_month} != {int(report_folder_basename.split('-')[0].strip())}") 
            return
        is_load_result = True
        al_result_create = data['create_al']
        al_result_update = data['update_al']
        cl_result_create = data['create_cl']
        cl_result_update = data['update_cl']
    except Exception as ex:
        print(ex)
        is_load_result = False
        al_result_create = {}
        al_result_update = {}
        cl_result_create = {}
        cl_result_update = {}

    is_load_df_old = (today.minute<12) and (today.minute>5)
    
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = True if current_month == today.month else False
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url=settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)
    file_model.export_sumary_attendance_report_ver2()
    file_model.export_al_cl_report_ho()
    file_model.export_kpi_weekly_report_ho()
    file_model.export_sumary_attendance_report_ho()
    file_model.export_late_in_5_miniutes_report_ho()

def export_report_department():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 10000 seconds: Export data All department")
    is_load_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        output_reportfolder_path = (data['folder_path'])
        report_folder_basename = os.path.basename(output_reportfolder_path)
        if (current_month != int(report_folder_basename.split('-')[0].strip())):
            print(f"{current_month} != {int(report_folder_basename.split('-')[0].strip())}") 
            return
        is_load_result = True
        al_result_create = data['create_al']
        al_result_update = data['update_al']
        cl_result_create = data['create_cl']
        cl_result_update = data['update_cl']
    except Exception as ex:
        print(ex)
        is_load_result = False
        al_result_create = {}
        al_result_update = {}
        cl_result_create = {}
        cl_result_update = {}

    is_load_df_old = (today.minute<12) and (today.minute>5)
    
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = True if current_month == today.month else False
   
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url=settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)
    
    file_model.export_sumary_attendance_report_department()
    # file_model.export_al_cl_report_department()
    file_model.export_attendence_scheduling_report_department()
    file_model.export_al_cl_report_severance()
    # file_model.export_sumary_attendance_report_ho()
def export_report_al_cl_next_month():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 10000 seconds: Export data All department")
    is_load_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        output_reportfolder_path = (data['folder_path'])
        report_folder_basename = os.path.basename(output_reportfolder_path)
        if (current_month != int(report_folder_basename.split('-')[0].strip())):
            print(f"{current_month} != {int(report_folder_basename.split('-')[0].strip())}") 
            return
        is_load_result = True
        al_result_create = data['create_al']
        al_result_update = data['update_al']
        cl_result_create = data['create_cl']
        cl_result_update = data['update_cl']
    except Exception as ex:
        print(ex)
        is_load_result = False
        al_result_create = {}
        al_result_update = {}
        cl_result_create = {}
        cl_result_update = {}

    is_load_df_old = (today.minute<12) and (today.minute>5)
    
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = True if current_month == today.month else False
   
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url=settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)
    
    file_model.export_al_cl_report_next_month()
    file_model.export_kpi_weekly_report()
    file_model.export_al_cl_report_severance()
    # file_model.export_sumary_attendance_report()
    

def export_report_next_month():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year + 1 if ((today.day >= 15) and (today.month == 12)) else today.year
    current_month = today.month + 1 if today.day >= 15 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    if current_month >= 13:
        current_month = current_month - 12

    print("this function runs every 3400 seconds: Load File")
    resource_path = "result-next-month.json"
    

    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True

    output_reportfolder_path = f'{current_month}-{today.minute}'
    isExist = os.path.exists(output_reportfolder_path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(output_reportfolder_path)
        print("The new output_report_folder is created! ", output_reportfolder_path)
    dst_file = os.path.join(output_reportfolder_path, 'old.xlsx')

    
    model = HrmExcelReport_v2(server_username= settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, \
        server_url=settings.SERVER_URL, \
        server_db= settings.SERVER_URL_DB,\
        start_date_str=startdate, end_date_str=enddate, ouput_report_folder= output_reportfolder_path, is_update_al_cl=True, \
        is_load_df_old = False)
    model.export_data_to_files()
    al_result_create = []
    al_result_update = []
    cl_result_create = []
    cl_result_update = []
    try:
        al_result_create = model.al_result_create
    except:
        pass
    try:
        al_result_update = model.al_result_update
    except:
        pass
    try:
        cl_result_create = model.cl_result_create
    except:
        pass
    try:
        cl_result_update = model.cl_result_update
    except:
        pass
    try:
        dictionary = {
            "folder_path": os.path.abspath(output_reportfolder_path).replace("\\",'/'),
            "today": today.strftime('%d-%m-%Y %H:%M:%S'),
            'create_al': al_result_create,
            'update_al': al_result_update,
            'create_cl': cl_result_create,
            'update_cl': cl_result_update
        }
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open(resource_path, "w") as outfile:
            outfile.write(json_object)
    except Exception as ex: 
        print(ex)
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url= settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, \
                is_update_al_cl=True, is_load_df_scheduling=is_update_scheduling, \
                minioClient = minioClient, public_url= public_url, bucket_name= bucket_name, 
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)

    try:
        file_model.export_sumary_attendance_report()
    except Exception as ex:
        print(" file_model.export_sumary_attendance_report()", ex)

    try:
        file_model.export_night_shift_report()
    except Exception as ex:
        print(" file_model.export_night_shift_report()", ex)
    try:
        file_model.export_late_in_5_miniutes_report()
    except Exception as ex:
        print('export_late_in_5_miniutes_report', ex)
    try:
        file_model.export_feed_report()
    except Exception as ex:
        print('export_feed_report', ex)
    # try:
    #     # file_model.export_al_cl_report()
    # except Exception as ex:
    #     print('export_al_cl_report', ex)
    try:
        file_model.export_attendence_scheduling_report()
    except Exception as ex:
        print('export_attendence_scheduling_report', ex)
    file_model.export_al_cl_report_severance()
def export_report_only():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 400 seconds: Load File")

    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        report_folder_basename = os.path.basename(data['folder_path'])
        if (current_month != int(report_folder_basename.split('-')[0].strip())):
            print(f"{current_month} != {int(report_folder_basename.split('-')[0].strip())}") 
            return
    except:
        print('ex load df old')
     
     

    is_load_df_old = False
    
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = True 
    
    output_reportfolder_path = f'{current_month}-{today.minute}'
    isExist = os.path.exists(output_reportfolder_path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(output_reportfolder_path)
        print("The new output_report_folder is created! ", output_reportfolder_path)
    dst_file = os.path.join(output_reportfolder_path, 'old.xlsx')
    if not is_load_df_old:
        try:
            if not os.path.samefile(src_file, dst_file):
                os.remove(dst_file)
        except Exception as ex:
            print("Remove ex", ex)
        try:
            shutil.copyfile(src_file, dst_file)
        except Exception as ex:
            print("copy ex", ex)

    
    model = HrmExcelReport_v2(server_username= settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, \
        server_url=settings.SERVER_URL, \
        server_db=settings.SERVER_URL_DB, \
        start_date_str=startdate, end_date_str=enddate, ouput_report_folder= output_reportfolder_path, is_update_al_cl=is_update_al_cl, \
        is_load_df_old = is_load_df_old)
    if is_load_df_old:
        model.auto_fill_missing_attendance_trans()
    model.export_data_to_files()
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    
    al_result_create = []
    al_result_update = []
    cl_result_create = []
    cl_result_update = []
    try:
        al_result_create = model.al_result_create
    except:
        pass
    try:
        al_result_update = model.al_result_update
    except:
        pass
    try:
        cl_result_create = model.cl_result_create
    except:
        pass
    try:
        cl_result_update = model.cl_result_update
    except:
        pass
    try:
        dictionary = {
            "folder_path": os.path.abspath(output_reportfolder_path).replace("\\",'/'),
            "today": today.strftime('%d-%m-%Y %H:%M:%S'),
            'create_al': al_result_create,
            'update_al': al_result_update,
            'create_cl': cl_result_create,
            'update_cl': cl_result_update
        }
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open(resource_path, "w") as outfile:
            outfile.write(json_object)
    except Exception as ex: 
        print(ex)
        
    # public_url = settings.MINIO_PUBLIC_URL
    # bucket_name = settings.MINIO_BUCKET_NAME
    
    # file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
    #             server_url= settings.SERVER_URL, \
    #             server_db= settings.SERVER_URL_DB,\
    #             server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
    #             ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
    #             minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
    #             create_al = al_result_create,
    #             update_al = al_result_update,
    #             create_cl = cl_result_create,
    #             update_cl = cl_result_update)
    # # file_model.export_al_cl_report()
    # try:
    #     file_model.export_sumary_attendance_report()
    # except Exception as ex:
    #     print(" file_model.export_sumary_attendance_report()", ex)
    # try:
    #     file_model.export_al_cl_report()
    # except Exception as ex:
    #     print(" file_model.export_al_cl_report()", ex)
    # try:
    #     file_model.export_night_shift_report()
    # except Exception as ex:
    #     print(" file_model.export_night_shift_report()", ex)
    # try:
    #     file_model.export_late_in_5_miniutes_report()
    # except Exception as ex:
    #     print('export_late_in_5_miniutes_report', ex)
    # # try:
    # file_model.export_feed_report()
    # # except Exception as ex:
    # #     print('export_feed_report', ex)

    # try:
    #     file_model.export_attendence_scheduling_report()
    # except Exception as ex:
    #     print('export_attendence_scheduling_report', ex)
        
def export_report():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 400 seconds: Load File")
    is_load_old_result = False
    try:
        resource_path = "result.json"
        f = open(resource_path)
        data = json.load(f)
        f.close()
        src_file = os.path.join(data['folder_path'], 'old.xlsx')
        is_load_old_result = True
       
    except:
        is_load_old_result = False
    

    # is_load_df_old = (today.minute<32) and (today.minute>5)
    is_load_df_old = False
    print(f"{current_year}, {current_month}")
    date_range = calendar.monthrange(current_year,current_month)
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = f'{"{:02d}".format(current_month)}/{"{:02d}".format(date_range[1])}/{current_year}'
    is_update_scheduling = True
    is_update_al_cl = False if is_load_df_old else True
    
    output_reportfolder_path = f'{current_month}-{today.minute}'
    isExist = os.path.exists(output_reportfolder_path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(output_reportfolder_path)
        print("The new output_report_folder is created! ", output_reportfolder_path)
    dst_file = os.path.join(output_reportfolder_path, 'old.xlsx')
    if (not is_load_df_old) and (is_load_old_result):
        try:
            if not os.path.samefile(src_file, dst_file):
                os.remove(dst_file)
        except Exception as ex:
            print("Remove ex", ex)
        try:
            shutil.copyfile(src_file, dst_file)
        except Exception as ex:
            print("copy ex", ex)

    
    model = HrmExcelReport_v2(server_username= settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, \
        server_url=settings.SERVER_URL, \
        server_db=settings.SERVER_URL_DB, \
        start_date_str=startdate, end_date_str=enddate, ouput_report_folder= output_reportfolder_path, is_update_al_cl=is_update_al_cl, \
        is_load_df_old = is_load_df_old)
    # if is_load_df_old:
    #     model.auto_fill_missing_attendance_trans()
    model.export_data_to_files()
    minioClient = Minio(
        settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY, secure=False
    )
    al_result_create = []
    al_result_update = []
    cl_result_create = []
    cl_result_update = []
    try:
        al_result_create = model.al_result_create
    except:
        pass
    try:
        al_result_update = model.al_result_update
    except:
        pass
    try:
        cl_result_create = model.cl_result_create
    except:
        pass
    try:
        cl_result_update = model.cl_result_update
    except:
        pass
    try:
        dictionary = {
            "folder_path": os.path.abspath(output_reportfolder_path).replace("\\",'/'),
            "today": today.strftime('%d-%m-%Y %H:%M:%S'),
            'create_al': al_result_create,
            'update_al': al_result_update,
            'create_cl': cl_result_create,
            'update_cl': cl_result_update
        }
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open(resource_path, "w") as outfile:
            outfile.write(json_object)
    except Exception as ex: 
        print(ex)
        
    public_url = settings.MINIO_PUBLIC_URL
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_model = HrmExcelFile(input_folder=output_reportfolder_path, start_date_str=startdate, end_date_str=enddate, \
                server_url= settings.SERVER_URL, \
                server_db= settings.SERVER_URL_DB,\
                server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD, is_calculate_late_early_leave=True, \
                ouput_report_folder=settings.CLOUD_OUTPUT_REPORT_FOLDER, is_load_df_old = False, is_load_df_scheduling=is_update_scheduling, \
                minioClient=minioClient,bucket_name=bucket_name, public_url=public_url,
                is_update_al_cl = is_update_al_cl,
                create_al = al_result_create,
                update_al = al_result_update,
                create_cl = cl_result_create,
                update_cl = cl_result_update)
    # # file_model.export_al_cl_report()
    # try:
    #     file_model.export_sumary_attendance_report()
    # except Exception as ex:
    #     print(" file_model.export_sumary_attendance_report()", ex)
    # # try:
    # #     # file_model.export_al_cl_report()
    # # except Exception as ex:
    # #     print(" file_model.export_al_cl_report()", ex)
    # try:
    #     file_model.export_night_shift_report()
    # except Exception as ex:
    #     print(" file_model.export_night_shift_report()", ex)
    # try:
    #     file_model.export_late_in_5_miniutes_report()
    # except Exception as ex:
    #     print('export_late_in_5_miniutes_report', ex)
    # # try:
    # file_model.export_feed_report()
    # # except Exception as ex:
    # #     print('export_feed_report', ex)

    # try:
    #     file_model.export_attendence_scheduling_report()
    # except Exception as ex:
    #     print('export_attendence_scheduling_report', ex)
    file_model.export_al_cl_report_severance()
    # # CLOUD_OUTPUT_REPORT_FOLDER = /Users/dungbui299/Dropbox/APECHRMS/OutputReport

def collect_attendance():
    if not check_server_avaiable():
        print('server PAUSED')
        return
    today = timezone.now()
    current_year = today.year -1 if ((today.day <=14) and (today.month == 1)) else today.year
    current_month = today.month-1 if today.day <=14 else today.month
    if current_month <= 0:
        current_month = current_month + 12
    print("this function runs every 60000 seconds: Load File")
   
    print(f"{current_year}, {current_month}")
    startdate = f'{"{:02d}".format(current_month)}/01/{current_year}'
    enddate = (today + datetime.timedelta(days=2)).strftime('%m/%d/%Y')
    print(f"{startdate}, {enddate}")
    input_folder = settings.CLOUD_OUTPUT_REPORT_FOLDER
    model = AttendenceReportModel(start_date_str=startdate, end_date_str=enddate, 
            server_url = settings.SERVER_URL, server_db = settings.SERVER_URL_DB, 
            server_username=settings.SERVER_USERNAME, server_password=SERVER_PASSWORD)
    # model.merge_download_attendance()
    model.update_attendance_from_csv(input_folder, df_time_recorder)
    model.update_attendance_ho_from_excel(input_folder, df_time_recorder)
    # model.update_attendance_from_ho_timekeeper()
    

