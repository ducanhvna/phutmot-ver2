import pandas as pd
from django.conf import settings
import os
from shutil import copyfile
from django.core.files.storage import default_storage

def nearest(items, pivot):
    print('item vao')
    print(items)
    return pd.to_datetime(min([i for i in items if i <= pivot], key=lambda x: abs(x - pivot)))

def float_to_hours(float_time_hour):
    float_time = round(float_time_hour * 60 * 2, -1)//2  # in minutes
    hours, seconds = divmod(float_time * 60, 3600)  # split to hours and seconds
    minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
    return int(hours), int(minutes), int(seconds)

def init_media_subfoder_report(user_name, sub_folder):
    media_dir = settings.MEDIA_ROOT
    output_report_folder = os.path.join(media_dir, 'output_report')
    isExist = os.path.exists(output_report_folder)
    if not isExist:
        os.makedirs(output_report_folder)
    output_report_folder = os.path.join(output_report_folder, user_name)
    isExist = os.path.exists(output_report_folder)
    if not isExist:
        os.makedirs(output_report_folder)
    output_report_folder = os.path.join(output_report_folder, sub_folder)
    isExist = os.path.exists(output_report_folder)
    if not isExist:
        os.makedirs(output_report_folder)
    return output_report_folder

# old_file_path = '/Users/dungbui299/Documents/github/black-dashboard-django-master 3/11-0/al_last_report.xlsx'
#     new_file_name = 'test.xlsx'
#     media_dir = settings.MEDIA_ROOT
    # print(media_dir)
def copy_to_default_storage(old_file_path, new_file_name, media_dir):
    new_file_path = os.path.join(media_dir, new_file_name)
    copyfile(old_file_path, new_file_path)
    # file = default_storage.open(new_file_name)
    file_url = default_storage.url(os.path.relpath(new_file_path, settings.MEDIA_ROOT))
    print(file_url)
    return file_url
