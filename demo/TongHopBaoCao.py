import json
import xmlrpc.client
import os
import pandas as pd
from datetime import datetime, timedelta
from lib.realtendant import odoo_login, get_employee_by_user_id

def get_production_report(start_date=None, end_date=None):
    """
    Tạo báo cáo sản xuất của nhân viên theo khoảng thời gian.
    Trả về danh sách thông tin chi tiết về nhân viên, máy, sản lượng trong ca làm.
    """
    if not start_date:
        # Mặc định lấy 7 ngày gần đây
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    uid, _, models = odoo_login()
    
    # Tìm các workorder trong khoảng thời gian
    domain = [
        ('date_start', '>=', start_date),
        ('date_start', '<=', end_date)
    ]
    workorder_ids = models.execute_kw('odoo', uid, 'admin', 'mrp.workorder', 'search', [domain])
    
    if not workorder_ids:
        return []
    
    # Lấy chi tiết workorder
    workorder_fields = [
        'id', 'name', 'date_start', 'date_finished', 'duration', 'qty_produced', 
        'workcenter_id', 'production_id', 'state'
    ]
    workorders = models.execute_kw('odoo', uid, 'admin', 'mrp.workorder', 'read', [workorder_ids, workorder_fields])
    
    result = []
    
    for wo in workorders:
        # Lấy productivity records để tìm nhân viên
        productivity_domain = [('workorder_id', '=', wo['id'])]
        productivity_ids = models.execute_kw('odoo', uid, 'admin', 'mrp.workcenter.productivity', 'search', [productivity_domain])
        
        if productivity_ids:
            productivity_fields = ['user_id', 'date_start', 'date_end', 'description']
            productivities = models.execute_kw('odoo', uid, 'admin', 'mrp.workcenter.productivity', 'read', [productivity_ids, productivity_fields])
            
            # Lấy thông tin scrap (phế phẩm)
            scrap_domain = [('workorder_id', '=', wo['id'])]
            scrap_ids = models.execute_kw('odoo', uid, 'admin', 'stock.scrap', 'search', [scrap_domain])
            scrapped_qty = 0
            if scrap_ids:
                scraps = models.execute_kw('odoo', uid, 'admin', 'stock.scrap', 'read', [scrap_ids, ['scrap_qty']])
                scrapped_qty = sum(scrap.get('scrap_qty', 0) for scrap in scraps)
            
            # Tính sản lượng thực tế
            actual_qty = wo.get('qty_produced', 0) - scrapped_qty
            
            # Tạo record cho từng user
            unique_users = {}
            for prod in productivities:
                user_id = prod.get('user_id')
                if user_id:
                    if isinstance(user_id, list):
                        user_id = user_id[0]
                    unique_users[user_id] = prod
            
            for user_id, prod in unique_users.items():
                # Lấy thông tin user
                try:
                    users = models.execute_kw('odoo', uid, 'admin', 'res.users', 'read', [[user_id], ['name', 'login']])
                    user_name = users[0].get('name', '') if users else f'User {user_id}'
                    user_code = users[0].get('login', '') if users else ''
                except:
                    user_name = f'User {user_id}'
                    user_code = ''
                
                # Lấy thông tin employee từ user_id
                employee_info = get_employee_by_user_id(user_id, fields=['id', 'name', 'barcode', 'identification_id'])
                if employee_info:
                    emp_name = employee_info.get('name', user_name)
                    emp_code = employee_info.get('barcode') or employee_info.get('identification_id', user_code)
                else:
                    emp_name = user_name
                    emp_code = user_code
                
                # Tạo record báo cáo
                workcenter_name = wo.get('workcenter_id', ['', ''])
                if isinstance(workcenter_name, list):
                    workcenter_name = workcenter_name[-1]
                
                result.append({
                    'date': wo.get('date_start', ''),
                    'employee_name': emp_name,
                    'employee_code': emp_code,
                    'user_id': user_id,
                    'workcenter': workcenter_name,
                    'operation': wo.get('name', ''),
                    'hours': wo.get('duration', 0),
                    'qty_produced': actual_qty,
                    'scrap_qty': scrapped_qty,
                    'note': '',
                    'state': wo.get('state', ''),
                    'workorder_id': wo.get('id')
                })
    
    return result

def get_contract_summary_report(start_date=None, end_date=None):
    """
    Tạo báo cáo tổng hợp công khoán của nhân viên theo khoảng thời gian.
    Trả về danh sách thông tin tổng hợp về nhân viên và tiền công khoán.
    """
    if not start_date:
        # Mặc định lấy 7 ngày gần đây
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    uid, _, models = odoo_login()
    
    # Tìm các productivity records trong khoảng thời gian
    domain = [
        ('date_start', '>=', start_date),
        ('date_start', '<=', end_date),
        ('user_id', '!=', False)  # Chỉ lấy những record có user_id
    ]
    productivity_ids = models.execute_kw('odoo', uid, 'admin', 'mrp.workcenter.productivity', 'search', [domain])
    
    if not productivity_ids:
        return []
    
    # Lấy chi tiết productivity
    productivity_fields = ['user_id', 'workorder_id', 'date_start', 'date_end', 'duration']
    productivities = models.execute_kw('odoo', uid, 'admin', 'mrp.workcenter.productivity', 'read', [productivity_ids, productivity_fields])
    
    # Group theo user_id
    user_data = {}
    
    for prod in productivities:
        user_id = prod.get('user_id')
        workorder_id = prod.get('workorder_id')
        duration = prod.get('duration', 0)
        
        if user_id and workorder_id:
            # Extract ID if it's a list
            if isinstance(user_id, list):
                u_id = user_id[0]
            else:
                u_id = user_id
                
            if isinstance(workorder_id, list):
                wo_id = workorder_id[0]
            else:
                wo_id = workorder_id
            
            if u_id not in user_data:
                user_data[u_id] = {
                    'workorders': set(),
                    'total_duration': 0.0,
                    'productivity_records': []
                }
            
            user_data[u_id]['workorders'].add(wo_id)
            user_data[u_id]['total_duration'] += duration
            user_data[u_id]['productivity_records'].append(prod)
    
    result = []
    
    for user_id, data in user_data.items():
        # Lấy thông tin user từ user_id
        try:
            users = models.execute_kw('odoo', uid, 'admin', 'res.users', 'read', [[user_id], ['name', 'login']])
            user_name = users[0].get('name', '') if users else f'User {user_id}'
            user_code = users[0].get('login', '') if users else ''
        except:
            user_name = f'User {user_id}'
            user_code = ''
        
        # Lấy thông tin employee từ user_id
        employee_info = get_employee_by_user_id(user_id, fields=['id', 'name', 'barcode', 'identification_id'])
        if employee_info:
            emp_name = employee_info.get('name', user_name)
            emp_code = employee_info.get('barcode') or employee_info.get('identification_id', user_code)
        else:
            emp_name = user_name
            emp_code = user_code
        
        # Lấy thông tin workorder để tính tổng sản lượng
        workorder_ids = list(data['workorders'])
        total_output = 0
        
        if workorder_ids:
            try:
                workorder_fields = ['qty_produced']
                workorders = models.execute_kw('odoo', uid, 'admin', 'mrp.workorder', 'read', [workorder_ids, workorder_fields])
                
                for wo in workorders:
                    total_output += wo.get('qty_produced', 0)
                    
            except Exception as e:
                print(f"Error getting workorder data: {e}")
        
        # Tính số lần đổi máy (số workorder khác nhau)
        machine_changes = len(data['workorders'])
        
        # Tổng giờ làm từ productivity duration (đã tính bằng phút, chuyển thành giờ)
        total_hours = round(data['total_duration'] / 60.0, 2)
        
        # Tính tiền công khoán (sản lượng * 525)
        contract_payment = total_output * 525
        
        result.append({
            'user_id': user_id,
            'employee_name': emp_name,
            'employee_code': emp_code,
            'machine_changes': machine_changes,
            'total_hours': total_hours,
            'total_output': total_output,
            'contract_payment': contract_payment
        })
    
    # Sắp xếp theo tên nhân viên
    result.sort(key=lambda x: x['employee_name'])
    
    return result

def export_production_report_to_excel(start_date=None, end_date=None, output_dir="Reports"):
    """
    Xuất báo cáo sản xuất ra file Excel
    """
    # Tạo thư mục output nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Lấy dữ liệu báo cáo
    report_data = get_production_report(start_date, end_date)
    
    if not report_data:
        print("Không có dữ liệu để xuất báo cáo")
        return None
    
    # Chuyển đổi sang DataFrame
    df = pd.DataFrame(report_data)
    
    # Đổi tên cột cho dễ đọc
    column_mapping = {
        'date': 'Ngày',
        'employee_name': 'Tên nhân viên',
        'employee_code': 'Mã nhân viên',
        'user_id': 'User ID',
        'workcenter': 'Máy/Khu vực',
        'operation': 'Công đoạn',
        'hours': 'Thời gian (giờ)',
        'qty_produced': 'Sản lượng',
        'scrap_qty': 'Phế phẩm',
        'note': 'Ghi chú',
        'state': 'Trạng thái',
        'workorder_id': 'ID Công đoạn'
    }
    
    df_renamed = df.rename(columns=column_mapping)
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"BaoCaoSanXuat_{start_date}_den_{end_date}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Xuất ra Excel với định dạng đẹp
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df_renamed.to_excel(writer, sheet_name='Báo cáo sản xuất', index=False)
        
        # Lấy worksheet để định dạng
        worksheet = writer.sheets['Báo cáo sản xuất']
        
        # Điều chỉnh độ rộng cột
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Đã xuất báo cáo thành công: {filepath}")
    return filepath

def get_workorder_summary_report(start_date=None, end_date=None):
    """
    Báo cáo tổng hợp theo công đoạn
    """
    report_data = get_production_report(start_date, end_date)
    
    if not report_data:
        return []
    
    # Tạo DataFrame để group by
    df = pd.DataFrame(report_data)
    
    # Group theo workorder và tính tổng
    summary = df.groupby(['operation', 'workcenter']).agg({
        'hours': 'sum',
        'qty_produced': 'sum',
        'scrap_qty': 'sum',
        'employee_name': 'count'  # Đếm số nhân viên
    }).reset_index()
    
    summary.columns = ['Công đoạn', 'Máy/Khu vực', 'Tổng thời gian (giờ)', 'Tổng sản lượng', 'Tổng phế phẩm', 'Số nhân viên']
    
    return summary.to_dict('records')

def get_employee_summary_report(start_date=None, end_date=None):
    """
    Báo cáo tổng hợp theo nhân viên
    """
    report_data = get_production_report(start_date, end_date)
    
    if not report_data:
        return []
    
    # Tạo DataFrame để group by
    df = pd.DataFrame(report_data)
    
    # Group theo nhân viên và tính tổng
    summary = df.groupby(['employee_name', 'employee_code']).agg({
        'hours': 'sum',
        'qty_produced': 'sum',
        'scrap_qty': 'sum',
        'operation': 'count'  # Đếm số công đoạn
    }).reset_index()
    
    summary.columns = ['Tên nhân viên', 'Mã nhân viên', 'Tổng thời gian (giờ)', 'Tổng sản lượng', 'Tổng phế phẩm', 'Số công đoạn']
    
    return summary.to_dict('records')

def export_all_reports_to_excel(start_date=None, end_date=None, output_dir="Reports"):
    """
    Xuất tất cả báo cáo ra một file Excel với nhiều sheet
    """
    # Tạo thư mục output nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Lấy dữ liệu các báo cáo
    detail_report = get_production_report(start_date, end_date)
    contract_summary = get_contract_summary_report(start_date, end_date)
    machine_summary = get_machine_summary_report(start_date, end_date)
    salary_comparison = get_salary_comparison_report(start_date, end_date)
    
    if not detail_report and not contract_summary and not machine_summary and not salary_comparison:
        print("Không có dữ liệu để xuất báo cáo")
        return None
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"TongHopBaoCaoSanXuat_{start_date}_den_{end_date}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Xuất ra Excel với nhiều sheet
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Sheet 1: Báo cáo chi tiết
        if detail_report:
            df_detail = pd.DataFrame(detail_report)
            column_mapping = {
                'date': 'Ngày',
                'employee_name': 'Tên nhân viên',
                'employee_code': 'Mã nhân viên',
                'user_id': 'User ID',
                'workcenter': 'Máy/Khu vực',
                'operation': 'Công đoạn',
                'hours': 'Thời gian (giờ)',
                'qty_produced': 'Sản lượng',
                'scrap_qty': 'Phế phẩm',
                'note': 'Ghi chú',
                'state': 'Trạng thái',
                'workorder_id': 'ID Công đoạn'
            }
            df_detail_renamed = df_detail.rename(columns=column_mapping)
            df_detail_renamed.to_excel(writer, sheet_name='Chi tiết sản xuất', index=False)
        
        # Sheet 2: Tổng hợp công khoán
        if contract_summary:
            df_contract = pd.DataFrame(contract_summary)
            contract_column_mapping = {
                'employee_code': 'Mã NV',
                'employee_name': 'Tên nhân viên',
                'machine_changes': 'Số lần đổi máy',
                'total_hours': 'Tổng giờ làm',
                'total_output': 'Tổng sản lượng',
                'contract_payment': 'Tiền công khoán (VNĐ)'
            }
            df_contract_renamed = df_contract.rename(columns=contract_column_mapping)
            df_contract_renamed.to_excel(writer, sheet_name='Tổng hợp công khoán', index=False)
        
        # Sheet 3: Báo cáo theo máy
        if machine_summary:
            df_machine = pd.DataFrame(machine_summary)
            machine_column_mapping = {
                'machine_name': 'Tên máy',
                'workorder_count': 'Lượt chuyền đến',
                'total_hours': 'Tổng giờ công',
                'total_output': 'Tổng sản lượng',
                'efficiency': 'Hiệu suất (sp/giờ)'
            }
            df_machine_renamed = df_machine.rename(columns=machine_column_mapping)
            df_machine_renamed.to_excel(writer, sheet_name='Báo cáo theo máy', index=False)
        
        # Sheet 4: Đối chiếu công khoán với bảng lương
        if salary_comparison:
            df_salary = pd.DataFrame(salary_comparison)
            salary_column_mapping = {
                'employee_name': 'Tên nhân viên',
                'employee_code': 'Mã NV',
                'contract_hours': 'Giờ công khoán',
                'standard_hours': 'Giờ công chuẩn',
                'contract_salary': 'Lương khoán',
                'total_salary': 'Lương thực nhận',
                'difference': 'Chênh lệch'
            }
            df_salary_renamed = df_salary.rename(columns=salary_column_mapping)
            df_salary_renamed.to_excel(writer, sheet_name='Đối chiếu công khoán với lương', index=False)
        
        # Định dạng các sheet
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            # Điều chỉnh độ rộng cột
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Đã xuất tổng hợp báo cáo thành công: {filepath}")
    return filepath

def get_machine_summary_report(start_date=None, end_date=None):
    """
    Tạo báo cáo tổng hợp theo máy sản xuất.
    Trả về danh sách thông tin tổng hợp về từng máy: lượt chuyền đến, tổng giờ công, tổng sản lượng, hiệu suất.
    """
    if not start_date:
        # Mặc định lấy 7 ngày gần đây
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    uid, _, models = odoo_login()
    
    # Tìm các workorder trong khoảng thời gian
    domain = [
        ('date_start', '>=', start_date),
        ('date_start', '<=', end_date),
        ('state', 'in', ['done', 'progress', 'ready'])  # Chỉ lấy workorder đã hoàn thành hoặc đang thực hiện
    ]
    workorder_ids = models.execute_kw('odoo', uid, 'admin', 'mrp.workorder', 'search', [domain])
    
    if not workorder_ids:
        return []
    
    # Lấy chi tiết workorder
    workorder_fields = [
        'id', 'name', 'workcenter_id', 'duration', 'qty_produced', 'qty_production', 'date_start', 'date_finished'
    ]
    workorders = models.execute_kw('odoo', uid, 'admin', 'mrp.workorder', 'read', [workorder_ids, workorder_fields])
    
    # Group theo workcenter (máy)
    machine_data = {}
    
    for wo in workorders:
        workcenter_id = wo.get('workcenter_id')
        if not workcenter_id:
            continue
            
        # Extract workcenter info
        if isinstance(workcenter_id, list):
            wc_id = workcenter_id[0]
            wc_name = workcenter_id[1]
        else:
            wc_id = workcenter_id
            wc_name = f"Workcenter {workcenter_id}"
        
        if wc_id not in machine_data:
            machine_data[wc_id] = {
                'name': wc_name,
                'workorders': [],
                'total_duration': 0.0,
                'total_output': 0,
                'total_planned': 0
            }
        
        # Tính duration (phút -> giờ)
        duration = wo.get('duration', 0) / 60.0 if wo.get('duration') else 0
        
        machine_data[wc_id]['workorders'].append(wo)
        machine_data[wc_id]['total_duration'] += duration
        machine_data[wc_id]['total_output'] += wo.get('qty_produced', 0)
        machine_data[wc_id]['total_planned'] += wo.get('qty_production', 0)
    
    result = []
    
    for wc_id, data in machine_data.items():
        # Số lượt chuyền đến = số workorder
        workorder_count = len(data['workorders'])
        
        # Tổng giờ công
        total_hours = round(data['total_duration'], 1)
        
        # Tổng sản lượng
        total_output = data['total_output']
        
        # Hiệu suất (sản phẩm/giờ)
        efficiency = round(total_output / total_hours, 0) if total_hours > 0 else 0
        
        result.append({
            'workcenter_id': wc_id,
            'machine_name': data['name'],
            'workorder_count': workorder_count,
            'total_hours': total_hours,
            'total_output': total_output,
            'efficiency': efficiency
        })
    
    # Sắp xếp theo tên máy
    result.sort(key=lambda x: x['machine_name'])
    
    return result

def get_salary_comparison_report(start_date=None, end_date=None):
    """
    Tạo báo cáo đối chiếu công khoán với bảng lương.
    Trả về danh sách thông tin tổng hợp về nhân viên, giờ công, và lương.
    """
    import calendar
    
    if not start_date:
        # Mặc định lấy tháng hiện tại
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        # Lấy đến ngày cuối tháng
        now = datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        end_date = now.replace(day=last_day).strftime("%Y-%m-%d")
    
    # Lấy dữ liệu công khoán (giờ công khoán = tổng giờ công từ máy)
    machine_data = get_machine_summary_report(start_date, end_date)
    contract_data = get_contract_summary_report(start_date, end_date)
    
    # Tính giờ công chuẩn (số ngày làm việc trong tháng)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Đếm số ngày làm việc (loại trừ T7, CN)
    working_days = 0
    current_date = start_dt
    while current_date <= end_dt:
        # 0=Monday, 6=Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            working_days += 1
        current_date += timedelta(days=1)
    
    # Giờ công chuẩn = số ngày làm việc * 8 giờ/ngày
    standard_hours = working_days * 8
    
    # Tạo dictionary để group theo nhân viên
    employee_salary_data = {}
    
    # Thu thập dữ liệu từ contract_data
    for record in contract_data:
        employee_name = record.get('employee_name', '')
        employee_code = record.get('employee_code', '')
        contract_hours = record.get('total_hours', 0)  # Giờ công khoán
        
        # Tính lương
        contract_salary = contract_hours * 525  # Lương khoán
        standard_salary = standard_hours * 400  # Lương chuẩn
        total_salary = contract_salary + standard_salary  # Lương thực nhận
        
        # Tính chênh lệch (Lương thực nhận - Lương khoán)
        difference = total_salary - contract_salary
        # difference = total_salary - (standard_hours * 400)
        
        employee_salary_data[employee_code] = {
            'employee_name': employee_name,
            'employee_code': employee_code,
            'contract_hours': contract_hours,
            'standard_hours': standard_hours,
            'contract_salary': contract_salary,
            'total_salary': total_salary,
            'difference': difference
        }
    
    # Chuyển đổi thành list và sắp xếp
    result = list(employee_salary_data.values())
    result.sort(key=lambda x: x['employee_name'])
    
    return result

# Test functions
if __name__ == "__main__":
    # Test báo cáo
    print("=== TEST BÁO CÁO SẢN XUẤT ===")
    
    # Lấy báo cáo 7 ngày gần đây
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Lấy báo cáo từ {start_date} đến {end_date}")
    
    # Lấy báo cáo chi tiết
    detail_report = get_production_report(start_date, end_date)
    print(f"Số bản ghi chi tiết: {len(detail_report)}")
    
    if detail_report:
        # Hiển thị 3 bản ghi đầu
        print("\n=== 3 BẢN GHI ĐẦU TIÊN ===")
        for i, record in enumerate(detail_report[:3]):
            print(f"{i+1}. {record['employee_name']} - {record['operation']} - {record['qty_produced']}")
        
        # Xuất Excel
        try:
            excel_file = export_all_reports_to_excel(start_date, end_date)
            print(f"\nĐã xuất báo cáo Excel: {excel_file}")
        except Exception as e:
            print(f"Lỗi khi xuất Excel: {e}")
    else:
        print("Không có dữ liệu báo cáo")
