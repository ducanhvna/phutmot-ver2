import pandas as pd
import os
from openpyxl import Workbook

def export_al_cl_report_department(data, output_dir, data_key='al_report'):
    """
    Xuất báo cáo AL/CL theo từng phòng ban, mỗi sheet là 1 phòng ban.
    """
    file_path = os.path.join(output_dir, 'al_cl_report_department.xlsx')
    df = data.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        # Nếu không có dữ liệu, tạo file rỗng
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Nếu có dữ liệu, group theo company_name, department_name
    with pd.ExcelWriter(file_path) as writer:
        grouped = df.groupby(['company_name', 'department_name'])
        for (company, dept), group in grouped:
            sheet_name = f"{company[:15]}_{dept[:10]}"
            # Excel sheet name max 31 ký tự, loại bỏ ký tự đặc biệt
            sheet_name = sheet_name.replace('/', '_').replace('\\', '_')[:31]
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_sumary_attendance_report(data, output_dir, data_key='attendance'):
    """
    Xuất báo cáo tổng hợp chấm công, mỗi sheet là 1 công ty.
    """
    file_path = os.path.join(output_dir, 'sumary_attendance_report.xlsx')
    df = data.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Nếu có dữ liệu, group theo company (hoặc trường phù hợp)
    if 'company' in df.columns:
        group_col = 'company'
    elif 'company_name' in df.columns:
        group_col = 'company_name'
    else:
        # Nếu không có cột group, xuất 1 sheet
        df.to_excel(file_path, index=False)
        return file_path

    with pd.ExcelWriter(file_path) as writer:
        for company, group in df.groupby(group_col):
            sheet_name = str(company)[:31].replace('/', '_').replace('\\', '_')
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_sumary_attendance_report_department(data, output_dir, data_key='attendance'):
    """
    Xuất báo cáo tổng hợp chấm công theo phòng ban, mỗi sheet là 1 phòng ban của 1 công ty.
    """
    file_path = os.path.join(output_dir, 'sumary_attendance_report_department.xlsx')
    df = data.get(data_key)
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Nếu có dữ liệu, group theo company, department (hoặc trường phù hợp)
    if 'company' in df.columns and 'department' in df.columns:
        group_cols = ['company', 'department']
    elif 'company_name' in df.columns and 'department_name' in df.columns:
        group_cols = ['company_name', 'department_name']
    else:
        # Nếu không có cột group, xuất 1 sheet
        df.to_excel(file_path, index=False)
        return file_path

    with pd.ExcelWriter(file_path) as writer:
        grouped = df.groupby(group_cols)
        for (company, dept), group in grouped:
            sheet_name = f"{str(company)[:15]}_{str(dept)[:10]}"
            sheet_name = sheet_name.replace('/', '_').replace('\\', '_')[:31]
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_late_in_5_miniutes_report_ho(data, output_dir):
    """
    Xuất báo cáo đi muộn dưới 5 phút cho khối HO, mỗi sheet là 1 công ty.
    """
    file_path = os.path.join(output_dir, 'late_in_5_miniutes_report_ho.xlsx')
    df = data.get('late_in_5_miniutes')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Group theo company hoặc company_name
    if 'company' in df.columns:
        group_col = 'company'
    elif 'company_name' in df.columns:
        group_col = 'company_name'
    else:
        # Nếu không có cột group, xuất 1 sheet
        df.to_excel(file_path, index=False)
        return file_path

    with pd.ExcelWriter(file_path) as writer:
        for company, group in df.groupby(group_col):
            sheet_name = str(company)[:31].replace('/', '_').replace('\\', '_')
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_feed_report(data, output_dir):
    """
    Xuất báo cáo tổng hợp ăn ca, mỗi sheet là 1 công ty.
    """
    file_path = os.path.join(output_dir, 'feed_report.xlsx')
    df = data.get('feed_report')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Group theo company hoặc company_name
    if 'company' in df.columns:
        group_col = 'company'
    elif 'company_name' in df.columns:
        group_col = 'company_name'
    else:
        # Nếu không có cột group, xuất 1 sheet
        df.to_excel(file_path, index=False)
        return file_path

    with pd.ExcelWriter(file_path) as writer:
        for company, group in df.groupby(group_col):
            sheet_name = str(company)[:31].replace('/', '_').replace('\\', '_')
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_kpi_weekly_report_ho(data, output_dir):
    """
    Xuất báo cáo KPI weekly cho khối HO, mỗi sheet là 1 công ty.
    """
    file_path = os.path.join(output_dir, 'kpi_weekly_report_ho.xlsx')
    df = data.get('kpi_weekly_report_summary')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path

    # Group theo company hoặc company_name
    if 'company' in df.columns:
        group_col = 'company'
    elif 'company_name' in df.columns:
        group_col = 'company_name'
    else:
        # Nếu không có cột group, xuất 1 sheet
        df.to_excel(file_path, index=False)
        return file_path

    with pd.ExcelWriter(file_path) as writer:
        for company, group in df.groupby(group_col):
            sheet_name = str(company)[:31].replace('/', '_').replace('\\', '_')
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_kpi_weekly_report(data, output_dir):
    file_path = os.path.join(output_dir, 'kpi_weekly_report.xlsx')
    df = data.get('kpi_weekly_report_summary')
    if isinstance(df, pd.DataFrame):
        df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report_ho(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report_ho.xlsx')
    df = data.get('al_report')
    if isinstance(df, pd.DataFrame):
        df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report.xlsx')
    df = data.get('al_report')
    if isinstance(df, pd.DataFrame):
        df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report_severance(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report_severance.xlsx')
    df = data.get('al_report')
    if isinstance(df, pd.DataFrame):
        df.to_excel(file_path, index=False)
    return file_path

# ... Các hàm export khác sẽ được bổ sung tương tự ...
