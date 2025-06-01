import pandas as pd
import os
from openpyxl import Workbook
from app.models.file_metadata import save_file_metadata_list
import openpyxl
from shutil import copyfile

def export_al_cl_report_department(data, output_dir, data_key='al_report'):
    """
    Xuất báo cáo AL/CL theo từng phòng ban, mỗi công ty là 1 file, file tổng sẽ ghép từ các file con.
    """
    df = data.get(data_key)
    if (
        not isinstance(df, pd.DataFrame)
        or df.empty
        or 'company_name' not in df.columns
        or 'department_name' not in df.columns
    ):
        # Nếu không có dữ liệu hoặc thiếu cột, tạo file tổng No Data
        file_path = os.path.join(output_dir, 'al_cl_report_department.xlsx')
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path
    # Tạo file cho từng công ty
    company_files = []
    for company, group_company in df.groupby('company_name'):
        safe_company = str(company)[:20].replace('/', '_').replace('\\', '_')
        file_path = os.path.join(output_dir, f"al_cl_report_department_{safe_company}.xlsx")
        with pd.ExcelWriter(file_path) as writer:
            for dept, group_dept in group_company.groupby('department_name'):
                if not group_dept.empty:
                    sheet_name = str(dept)[:31].replace('/', '_').replace('\\', '_')
                    group_dept.to_excel(writer, sheet_name=sheet_name, index=False)
        company_files.append(file_path)
    # Ghép các file con thành file tổng (nhiều sheet, mỗi sheet là 1 công ty)
    import openpyxl
    file_path = os.path.join(output_dir, 'al_cl_report_department.xlsx')
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for company, group_company in df.groupby('company_name'):
            # Gộp toàn bộ dữ liệu công ty vào 1 sheet
            sheet_name = str(company)[:31].replace('/', '_').replace('\\', '_')
            group_company.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path

def export_sumary_attendance_report_department(data, output_dir, data_key='attendance'):
    """
    Xuất báo cáo tổng hợp chấm công theo phòng ban, mỗi sheet là 1 phòng ban của 1 công ty.
    """
    file_path = os.path.join(output_dir, 'sumary_attendance_report_department.xlsx')
    df = data.get(data_key)
    with pd.ExcelWriter(file_path) as writer:
        if not isinstance(df, pd.DataFrame) or df.empty:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        else:
            # Nếu có dữ liệu, group theo company, department (hoặc trường phù hợp)
            if 'company' in df.columns and 'department' in df.columns:
                group_cols = ['company', 'department']
            elif 'company_name' in df.columns and 'department_name' in df.columns:
                group_cols = ['company_name', 'department_name']
            else:
                df.to_excel(writer, sheet_name='No Data', index=False)
                return file_path
            has_data = False
            grouped = df.groupby(group_cols)
            for (company, dept), group in grouped:
                if not group.empty:
                    sheet_name = f"{str(company)[:15]}_{str(dept)[:10]}"
                    sheet_name = sheet_name.replace('/', '_').replace('\\', '_')[:31]
                    group.to_excel(writer, sheet_name=sheet_name, index=False)
                    has_data = True
            if not has_data:
                pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
    return file_path

def export_late_in_5_miniutes_report(data, output_dir):
    """
    Xuất báo cáo đi muộn dưới 5 phút, mỗi công ty là 1 file riêng biệt.
    """
    # Hỗ trợ cả trường hợp data là dict chứa DataFrame hoặc trực tiếp là DataFrame
    df = data.get('late_in_5_miniutes') if isinstance(data, dict) else data
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        file_path = os.path.join(output_dir, 'late_in_5_miniutes_report_No_Data.xlsx')
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return [file_path]
    # Xác định cột group theo công ty
    if 'company' in df.columns:
        group_col = 'company'
    elif 'company_name' in df.columns:
        group_col = 'company_name'
    else:
        file_path = os.path.join(output_dir, 'late_in_5_miniutes_report_No_Group.xlsx')
        df.to_excel(file_path, index=False)
        return [file_path]
    file_paths = []
    for company, group in df.groupby(group_col):
        if not group.empty:
            safe_company = str(company)[:20].replace('/', '_').replace('\\', '_')
            file_path = os.path.join(output_dir, f"late_in_5_miniutes_report_{safe_company}.xlsx")
            with pd.ExcelWriter(file_path) as writer:
                group.to_excel(writer, sheet_name='Data', index=False)
            file_paths.append(file_path)
    if not file_paths:
        file_path = os.path.join(output_dir, 'late_in_5_miniutes_report_No_Data.xlsx')
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return [file_path]
    return file_paths

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
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path
    df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report_ho(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report_ho.xlsx')
    df = data.get('al_report')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path
    df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report.xlsx')
    df = data.get('al_report')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path
    df.to_excel(file_path, index=False)
    return file_path

def export_al_cl_report_severance(data, output_dir):
    file_path = os.path.join(output_dir, 'al_cl_report_severance.xlsx')
    df = data.get('al_report')
    if not isinstance(df, pd.DataFrame) or df.empty:
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return file_path
    df.to_excel(file_path, index=False)
    return file_path

def export_json_report(data: dict, output_dir: str, file_name: str):
    """
    Lưu dict chuẩn hóa ra file json với tên file_name trong output_dir.
    Tự động chuyển các kiểu datetime, Timestamp, numpy types về string hoặc native cho JSON.
    """
    import json
    import numpy as np
    import pandas as pd
    from datetime import datetime, date
    def default_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, dict)):
            return list(obj)
        return str(obj)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=default_serializer)
    return file_path

def export_summary_attendance_report(data, output_dir, data_key=None, template_path=None, date_array=None):
    """
    Xuất báo cáo tổng hợp chấm công từng công ty, sử dụng template Excel chuẩn.
    Mỗi công ty là 1 file, sheet đầu tiên sẽ được ghi dữ liệu tổng hợp.
    """
    import pandas as pd
    import openpyxl
    from shutil import copyfile
    import os
    from datetime import datetime, timedelta
    import calendar
    # Tự động chọn data_key nếu không truyền vào
    if data_key is None:
        if 'apec_attendance_report' in data:
            data_key = 'apec_attendance_report'
        elif 'attendance' in data:
            data_key = 'attendance'
        else:
            raise ValueError("Không tìm thấy key dữ liệu phù hợp trong dict data!")
    if template_path is None:
        template_path = os.path.join(os.path.dirname(__file__), 'template', 'Summary time attendant OK.xlsx')
    df = data.get(data_key)
    file_paths = []
    if not isinstance(df, pd.DataFrame) or df.empty:
        file_path = os.path.join(output_dir, 'summary_attendance_report_No_Data.xlsx')
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return [file_path]
    # Xác định cột group theo công ty
    group_col = 'mis_id' if 'mis_id' in df.columns else 'company_name' if 'company_name' in df.columns else None
    if not group_col:
        file_path = os.path.join(output_dir, 'summary_attendance_report_No_Group.xlsx')
        df.to_excel(file_path, index=False)
        return [file_path]
    # Nếu date_array không truyền vào thì lấy từ ngày đầu tháng đến cuối tháng hiện tại
    if date_array is None:
        now = datetime.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1], hour=0, minute=0, second=0, microsecond=0)
        date_array = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    for company, group in df.groupby(group_col):
        if not group.empty:
            safe_company = str(company)[:20].replace('/', '_').replace('\\', '_')
            file_path = os.path.join(output_dir, f"summary_attendance_report_{safe_company}.xlsx")
            copyfile(template_path, file_path)
            wb = openpyxl.load_workbook(file_path)
            ws = wb.worksheets[0]
            # Merge và ghi thông tin công ty, ngày tháng lên đầu file
            ws.merge_cells('C2:Z2')
            ws['C2'].value = company
            ws.merge_cells('C3:Z3')
            ws['C3'].value = ''
            ws.merge_cells('C4:Z4')
            ws['C4'].value = ''
            ws.merge_cells('A6:BK6')
            ws['A6'].value = f'Employee Type: All - Working Time: All - Pay Cycle: Month - Payment Period: {date_array[0].strftime("%d/%m/%Y")} - {date_array[-1].strftime("%d/%m/%Y")}'
            start_row = 11
            start_col = 33
            for date_item in date_array:
                day_of_month = date_item.day
                ws.cell(row=start_row-1, column=start_col + day_of_month).value = date_item
                ws.cell(row=start_row-2, column=start_col + day_of_month).value = date_item.strftime('%A')[:3]
            if date_array and date_array[-1].day < 31:
                for add_item in range(date_array[-1].day + 1, 32):
                    ws.cell(row=start_row-1, column=start_col + add_item).value = ''
                    ws.cell(row=start_row-2, column=start_col + add_item).value = ''
                    ws.cell(row=start_row, column=start_col + add_item).value = ''
            # Ghi dữ liệu từng nhân viên: name vào cột 3, employee_code vào cột 2
            for sub_group_index, sub_group_data in group.groupby(['name', 'employee_code']):
                ws.cell(row=start_row, column=2).value = sub_group_index[1]
                ws.cell(row=start_row, column=3).value = sub_group_index[0]
                # Ghi các trường còn lại nếu cần (ví dụ: tổng hợp theo ngày, v.v.)
                # ...
                start_row += 1
            wb.save(file_path)
            file_paths.append(file_path)
    if not file_paths:
        file_path = os.path.join(output_dir, 'summary_attendance_report_No_Data.xlsx')
        with pd.ExcelWriter(file_path) as writer:
            pd.DataFrame().to_excel(writer, sheet_name='No Data', index=False)
        return [file_path]
    return file_paths
