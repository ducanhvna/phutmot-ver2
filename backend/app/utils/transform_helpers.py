import pandas as pd
from datetime import timedelta, datetime
import calendar

def float_to_hours(float_time_hour):
    """
    Chuyển đổi số thực giờ (float) sang tuple (giờ, phút, giây).
    Ví dụ: 8.5 -> (8, 30, 0)
    """
    if float_time_hour is None or pd.isnull(float_time_hour):
        return 0, 0, 0
    try:
        h = int(float_time_hour)
        m = int((float_time_hour - h) * 60)
        s = int(round(((float_time_hour - h) * 60 - m) * 60))
        return h, m, s
    except Exception:
        return 0, 0, 0

def add_name_field(data_list, id_field='company_id', name_field=None):
    """
    Bổ sung trường *_name cho mỗi dict trong data_list dựa vào id_field dạng [id, name].
    Nếu không có hoặc lỗi, gán False.
    id_field: tên trường id (vd: company_id, department_id, ...)
    name_field: tên trường name muốn thêm, nếu None sẽ tự động là id_field thay '_id' cuối cùng bằng '_name'.
    """
    if not id_field.endswith('_id'):
        raise ValueError('id_field phải kết thúc bằng _id')
    if name_field is None:
        name_field = id_field[:-3] + '_name'
    for item in data_list:
        try:
            name_value = item[id_field][1]
            item[name_field] = name_value
            item[id_field] = item[id_field][0]
        except Exception:
            item[name_field] = False
    return data_list

def calculate_actual_work_time_ho_row(row):
    """
    Tính tổng thời gian làm việc thực tế cho 1 dòng dữ liệu attendance HO.
    row: dict hoặc Series, cần có các trường 'couple', 'attendance_attempt_{i}', ...
    Trả về tổng số phút làm việc thực tế (int).
    """
    result = 0
    def calculate_actual_work_time_couple(row, real_time_in, real_time_out):
        # Hàm phụ, copy từ logic của HrmExcelFile.calculate_actual_work_time_couple
        night_work_time = 0
        fix_rest_time = row.get('fix_rest_time', False)
        try:
            if (real_time_in is None) or (real_time_in == '') or (real_time_out is None) or (real_time_out == ''):
                res = 0
            else:
                start_work_date_time = row['shift_start_datetime'].replace(second=0)
                end_work_date_time = row['shift_end_datetime'].replace(second=0)
                start_rest_date_time = row['rest_start_datetime'].replace(second=0)
                end_rest_date_time = row['rest_end_datetime'].replace(second=0)
                current_program = min(real_time_out.replace(second=0), start_rest_date_time) - max(real_time_in.replace(second=0), start_work_date_time)
                stage_fist = max(0, current_program.total_seconds()//60.0)
                current_program = min(real_time_out.replace(second=0), end_work_date_time) - max(real_time_in.replace(second=0), end_rest_date_time)
                stage_second = max(0, current_program.total_seconds()//60.0)
                res = int(stage_fist + stage_second)
                if fix_rest_time:
                    res = min(res, 480)
        except Exception:
            res = 0
        return {'total_work_time': res, 'night_hours_normal': night_work_time}
    # Xử lý từng couple
    couples = row.get('couple', [])
    if isinstance(couples, list) and len(couples) > 0 and isinstance(couples[0], list):
        couples = couples[0]
    for couple in couples:
        if len(couple) < 2:
            continue
        in_index = couple[0]
        out_index = couple[1]
        real_time_in = row.get(f'attendance_attempt_{in_index}')
        real_time_out = row.get(f'attendance_attempt_{out_index}')
        update_data_item = calculate_actual_work_time_couple(row, real_time_in, real_time_out)
        result += update_data_item['total_work_time']
    return result

def process_report_raw(row):
    """
    Tính toán và sinh các trường datetime liên quan đến ca làm việc cho 1 dòng báo cáo chấm công.
    Đầu vào: row (dict hoặc Series) cần có các trường: date, start_work_time, end_work_time, start_rest_time, end_rest_time, shift_start, shift_end, rest_start, rest_end
    Đầu ra: tuple (shift_start_datetime, shift_end_datetime, rest_start_datetime, rest_end_datetime)
    """
    shift_start_datetime = None
    shift_end_datetime = None
    rest_start_datetime = None
    rest_end_datetime = None
    try:
        start_work_time = row.get('start_work_time', None)
        if pd.isnull(start_work_time) or start_work_time is None:
            start_work_time = row.get('shift_start', None)
        end_work_time = row.get('end_work_time', None)
        if pd.isnull(end_work_time) or end_work_time is None:
            end_work_time = row.get('shift_end', None)
        start_rest_time = row.get('start_rest_time', None)
        if pd.isnull(start_rest_time) or start_rest_time is None:
            start_rest_time = row.get('rest_start', None)
        end_rest_time = row.get('end_rest_time', None)
        if pd.isnull(end_rest_time) or end_rest_time is None:
            end_rest_time = row.get('rest_end', None)
        h, m, s = float_to_hours(start_work_time)
        shift_start_datetime = row['date'].replace(hour=h, minute=m, second=s)
        h, m, s = float_to_hours(end_work_time)
        shift_end_datetime = row['date'].replace(hour=h, minute=m, second=s)
        if end_work_time is not None and start_work_time is not None and end_work_time < start_work_time:
            shift_end_datetime = shift_end_datetime + timedelta(days=1)
        h, m, s = float_to_hours(start_rest_time)
        rest_start_datetime = row['date'].replace(hour=h, minute=m, second=s)
        if start_rest_time is not None and start_work_time is not None and start_rest_time < start_work_time:
            rest_start_datetime = rest_start_datetime + timedelta(days=1)
        h, m, s = float_to_hours(end_rest_time)
        rest_end_datetime = row['date'].replace(hour=h, minute=m, second=s)
        if end_rest_time is not None and start_work_time is not None and end_rest_time < start_work_time:
            rest_end_datetime = rest_end_datetime + timedelta(days=1)
    except Exception as ex:
        # Có thể log lỗi nếu cần
        pass
    return shift_start_datetime, shift_end_datetime, rest_start_datetime, rest_end_datetime

def find_couple(row, list_out_leave_for_work=None):
    """
    Sinh trường 'couple' cho 1 dòng báo cáo chấm công (apec_attendance_report).
    Nếu list_out_leave_for_work không truyền vào thì mặc định là [].
    Trả về list các cặp (in_index, out_index) ứng với các lần vào/ra hợp lệ.
    """
    result = [[]]
    time_stack = []
    flags = []
    for index in range(1, 16):
        flags.append('')
    if list_out_leave_for_work is None:
        list_out_leave_for_work = []
    for leave_item in list_out_leave_for_work:
        min_delete_index = 16
        max_delete_index = -1
        for index in range(15, 0, -1):
            att_attempt = row.get(f'attendance_attempt_{index}')
            if att_attempt is not None and \
                leave_item.get('attendance_missing_from') is not None and \
                leave_item.get('attendance_missing_to') is not None and \
                (att_attempt >= leave_item['attendance_missing_from']) and \
                (att_attempt <= leave_item['attendance_missing_to']):
                flags[index] = 'x'  # delete
            if min_delete_index < index:
                min_delete_index = index
            if max_delete_index < index:
                max_delete_index = index
        # (logic xóa các attendance theo flags nếu cần)
    for index in range(1, 16):
        attendance_attempt = row.get(f'attendance_attempt_{index}')
        attendance_inout = row.get(f'attendance_inout_{index}')
        if attendance_inout == 'I':
            time_stack.append(index)
        elif attendance_inout == 'O':
            if len(time_stack) > 0:
                result[0].append((time_stack[len(time_stack) - 1], index))
            time_stack = []
    return result

def find_couple_out_in_row(row):
    """
    Tìm các cặp (O, I) và tổng số phút out_ho cho 1 dòng báo cáo chấm công (apec_attendance_report).
    Trả về tuple (couple_out_in, total_out_ho)
    """
    result = [[]]
    time_stack = []
    flags = []
    total_out_minute = 0
    for index in range(1, 16):
        flags.append('')
    for index in range(1, 16):
        attendance_attempt = row.get(f'attendance_attempt_{index}')
        attendance_inout = row.get(f'attendance_inout_{index}')
        if attendance_inout == 'O':
            time_stack.append(index)
        elif attendance_inout == 'I':
            if len(time_stack) > 0:
                result[0].append((time_stack[-1], index))
                in_index = time_stack[-1]
                out_index = index
                real_time_in = row.get(f'attendance_attempt_{in_index}')
                real_time_out = row.get(f'attendance_attempt_{out_index}')
                update_data_item = calculate_actual_work_time_couple_for_out_in(row, real_time_in, real_time_out)
                total_out_minute += update_data_item['total_work_time']
            time_stack = []
    return result, total_out_minute

def calculate_actual_work_time_couple_for_out_in(row, real_time_in, real_time_out):
    """
    Hàm phụ trợ tính thời gian làm việc thực tế cho 1 cặp out-in (O-I).
    """
    night_work_time = 0
    fix_rest_time = row.get('fix_rest_time', False)
    try:
        if (real_time_in is None) or (real_time_in == '') or (real_time_out is None) or (real_time_out == ''):
            res = 0
        else:
            start_work_date_time = row['shift_start_datetime'].replace(second=0)
            end_work_date_time = row['shift_end_datetime'].replace(second=0)
            start_rest_date_time = row['rest_start_datetime'].replace(second=0)
            end_rest_date_time = row['rest_end_datetime'].replace(second=0)
            current_program = min(real_time_out.replace(second=0), start_rest_date_time) - max(real_time_in.replace(second=0), start_work_date_time)
            stage_fist = max(0, current_program.total_seconds()//60.0)
            current_program = min(real_time_out.replace(second=0), end_work_date_time) - max(real_time_in.replace(second=0), end_rest_date_time)
            stage_second = max(0, current_program.total_seconds()//60.0)
            res = int(stage_fist + stage_second)
            if fix_rest_time:
                res = min(res, 480)
    except Exception:
        res = 0
    return {'total_work_time': res, 'night_hours_normal': night_work_time}

def transform_apec_attendance_report(df, df_old=None):
    """
    Transform cho df apec_attendance_report: sinh couple, couple_out_in, tổng out_ho, các trường datetime, attendance_attempt, ...
    df_old: DataFrame chứa dữ liệu gốc để mapping attendance_attempt nếu cần
    """
    if df.empty:
        return df
    # Sinh các trường datetime ca làm việc
    df[['shift_start_datetime','shift_end_datetime', 'rest_start_datetime', 'rest_end_datetime']] = df.apply(process_report_raw, axis=1, result_type='expand')
    # Sinh couple (I-O)
    df['couple'] = df.apply(lambda row: find_couple_row(row), axis=1)
    # Sinh couple_out_in (O-I) và tổng out_ho
    df[['couple_out_in', 'total_out_ho']] = df.apply(lambda row: pd.Series(find_couple_out_in_row(row)), axis=1)
    # Nếu có df_old, sinh các trường attendance_attempt, attendance_inout, last_attendance_attempt, night_shift...
    if df_old is not None:
        df[['has_attendance', 'min_time_out', 'max_time_in']] = df.apply(lambda row: pd.Series(get_scheduling_time_row(row, df_old)), axis=1)
    if 'couple' in df.columns:
            df['actual_work_time_ho'] = df.apply(calculate_actual_work_time_ho_row, axis=1)
    return df

def find_couple_row(row):
    """
    Hàm sinh couple (I-O) cho 1 dòng, tương tự find_couple nhưng không cần list_out_leave_for_work.
    """
    result = [[]]
    time_stack = []
    for index in range(1, 16):
        attendance_attempt = row.get(f'attendance_attempt_{index}')
        attendance_inout = row.get(f'attendance_inout_{index}')
        if attendance_inout == 'I':
            time_stack.append(index)
        elif attendance_inout == 'O':
            if len(time_stack) > 0:
                result[0].append((time_stack[-1], index))
            time_stack = []
    return result

def get_scheduling_time_row(row, df_old):
    """
    Sinh các trường attendance_attempt_{i}, attendance_inout_{i}, last_attendance_attempt, night_shift,... cho 1 dòng từ df_old.
    Trả về tuple (has_attendance, min_time_out, max_time_in)
    """
    import pandas as pd
    has_attendance = False
    min_time_out = None
    max_time_in = None
    data = df_old[(df_old['Ngày'] == row['date_str']) & (df_old['time_keeping_code'] == row['time_keeping_code'])]
    update_data = {f'attendance_attempt_{i}': False for i in range(1, 16)}
    update_data.update({f'attendance_inout_{i}': False for i in range(1, 16)})
    update_data['last_attendance_attempt'] = False
    update_data['night_shift'] = False
    t_fist = None
    t_last = None
    t_mid_array = []
    inout_mid_array = []
    len_df = len(data['Giờ']) if 'Giờ' in data else 0
    if len_df > 1:
        t_last = data.iloc[len_df - 1]['Giờ']
    index_col = 1
    if len_df > 0:
        t_fist = data.iloc[0]['Giờ']
        for idx, item in data.iterrows():
            update_data[f'attendance_attempt_{index_col}'] = item['Giờ']
            update_data[f'attendance_inout_{index_col}'] = item['in_out']
            if item['Giờ'] != t_fist and item['Giờ'] != t_last:
                t_mid_array.append(item['Giờ'])
                inout_mid_array.append(item['in_out'])
            update_data['last_attendance_attempt'] = item['Giờ']
            index_col = min(15, index_col + 1)
    max_time_in = t_fist
    # Sinh couple
    update_data['couple'] = find_couple_row(update_data)
    update_data['fix_rest_time'] = row['fix_rest_time'] if pd.notnull(row['fix_rest_time']) else False
    try:
        if max_time_in is not None and max_time_in.replace(second=0) < row['shift_start_datetime']:
            max_time_in = max([a for a in data['Giờ'] if a.replace(second=0) <= row['shift_start_datetime']])
    except Exception as ex:
        print("nho ti ti: ", ex)
    min_time_out = t_last
    try:
        if min_time_out is not None and min_time_out.replace(second=0) > row['shift_end_datetime']:
            min_time_out = min([a for a in data['Giờ'] if a.replace(second=0) >= row['shift_end_datetime']])
    except Exception as ex:
        print("Hoi kho nhi: ", ex)
    update_data['id'] = row['id']
    update_data['shift_name'] = row['shift_name']
    update_data['rest_shift'] = row['rest_shift']
    update_data['total_shift_work_time'] = row['total_shift_work_time']
    update_data['shift_start_datetime'] = row['shift_start_datetime']
    update_data['shift_end_datetime'] = row['shift_end_datetime']
    update_data['rest_start_datetime'] = row['rest_start_datetime']
    update_data['rest_end_datetime'] = row['rest_end_datetime']
    # Tính actual_work_time_ho
    update_data_result = calculate_actual_work_time_ho_row(update_data)
    # Trả về tuple (has_attendance, min_time_out, max_time_in)
    return has_attendance, min_time_out, max_time_in

def add_mis_id_by_company_id(data, companies):
    """
    Bổ sung trường mis_id vào data (list[dict] hoặc DataFrame) dựa vào company_id, mapping từ companies (list[dict] hoặc DataFrame).
    """
    # Chuẩn hóa companies thành dict: id -> mis_id
    if isinstance(companies, pd.DataFrame):
        company_map = {row['id']: row['mis_id'] for _, row in companies.iterrows() if 'id' in row and 'mis_id' in row}
    else:
        company_map = {c['id']: c.get('mis_id') for c in companies if 'id' in c}
    # Xử lý cho list dict
    if isinstance(data, list):
        for item in data:
            cid = None
            if isinstance(item.get('company_id'), (list, tuple)) and len(item['company_id']) > 0:
                cid = item['company_id'][0]
            elif isinstance(item.get('company_id'), int):
                cid = item['company_id']
            if cid is not None and cid in company_map:
                item['mis_id'] = company_map[cid]
            else:
                item['mis_id'] = None
        return data
    # Xử lý cho DataFrame
    elif isinstance(data, pd.DataFrame) and 'company_id' in data.columns:
        def get_cid(val):
            if isinstance(val, (list, tuple)) and len(val) > 0:
                return val[0]
            return val
        data['mis_id'] = data['company_id'].apply(lambda cid: company_map.get(get_cid(cid), None))
        return data
    return data

def add_mis_id_by_company_name(data, companies):
    """
    Bổ sung trường mis_id vào data (list[dict] hoặc DataFrame) dựa vào company_name, mapping từ companies (list[dict] hoặc DataFrame).
    """
    # Chuẩn hóa companies thành dict: name -> mis_id
    name_col = 'company'
    if isinstance(data, pd.DataFrame):
        name_col = 'company' if 'company' in data.columns else 'company_name'
    if isinstance(companies, pd.DataFrame):
        company_map = {row['name']: row['mis_id'] for _, row in companies.iterrows() if 'name' in row and 'mis_id' in row}
    else:
        company_map = {c['name']: c.get('mis_id') for c in companies if 'name' in c}
    # Xử lý cho list dict
    if isinstance(data, list):
        for item in data:
            cname = item.get(name_col)
            if cname is not None and cname in company_map:
                item['mis_id'] = company_map[cname]
            else:
                item['mis_id'] = None
        return data
    # Xử lý cho DataFrame
    elif isinstance(data, pd.DataFrame) and name_col in data.columns:
        data['mis_id'] = data[name_col].apply(lambda cname: company_map.get(cname, None))
        return data
    return data

def employees_list_to_dict(df_emp):
    """
    Chuyển DataFrame employees về dict theo code (bỏ các dòng không có code).
    Mỗi code là 1 dict với key 'profiles' chứa list các dict profile (các dòng cùng code).
    """
    if df_emp is None or df_emp.empty or "code" not in df_emp.columns:
        return {}
    df_emp = df_emp.dropna(subset=["code"])
    emp_dict = {}
    for code, group in df_emp.groupby("code"):
        profiles = group.to_dict(orient="records")
        emp_dict[code] = {"profiles": profiles}
    return emp_dict

def contracts_list_to_dict(df_contracts, enddate=None):
    """
    Chuẩn hóa contracts thành dict theo employee_code:
    - contracts: list hợp đồng trong khoảng thời gian (lọc theo date_start, date_end)
    - main_contract: hợp đồng mới nhất tính đến thời điểm enddate (date_start <= enddate, date_end >= enddate hoặc null)
    """
    if df_contracts is None or df_contracts.empty or "employee_code" not in df_contracts.columns:
        return {}
    contracts_dict = {}
    for code, group in df_contracts.groupby("employee_code"):
        contracts = group.sort_values("date_start").to_dict(orient="records")
        main_contract = None
        if enddate is not None:
            # Lấy hợp đồng mới nhất có date_start <= enddate và (date_end >= enddate hoặc date_end null)
            group_valid = group[(group["date_start"] <= enddate) & ((group["date_end"].isnull()) | (group["date_end"] >= enddate))]
            if not group_valid.empty:
                main_contract = group_valid.sort_values("date_start").iloc[-1].to_dict()
        contracts_dict[code] = {
            "contracts": contracts,
            "main_contract": main_contract
        }
    return contracts_dict

def leaves_list_to_dict(df_leaves):
    """
    Chuẩn hóa leaves thành dict theo employee_code: mỗi key là employee_code, value là list các đơn nghỉ phép.
    """
    if df_leaves is None or df_leaves.empty or "employee_code" not in df_leaves.columns:
        return {}
    leaves_dict = {}
    for code, group in df_leaves.groupby("employee_code"):
        leaves_dict[code] = group.to_dict(orient="records")
    return leaves_dict

def kpi_weekly_report_summary_list_to_dict(df_kpi):
    """
    Chuẩn hóa kpi_weekly_report_summary thành dict theo employee_code:
    - Mỗi key là employee_code, value là list các bản ghi kpi_weekly_report_summary tương ứng.
    """
    if df_kpi is None or df_kpi.empty or "employee_code" not in df_kpi.columns:
        return {}
    kpi_dict = {}
    for code, group in df_kpi.groupby("employee_code"):
        kpi_dict[code] = group.to_dict(orient="records")
    return kpi_dict

def hr_weekly_report_list_to_dict(df_hr):
    """
    Chuẩn hóa hr_weekly_report thành dict theo employee_code:
    - Mỗi key là employee_code, value là list các bản ghi hr_weekly_report tương ứng.
    """
    if df_hr is None or df_hr.empty or "employee_code" not in df_hr.columns:
        return {}
    hr_dict = {}
    for code, group in df_hr.groupby("employee_code"):
        hr_dict[code] = group.to_dict(orient="records")
    return hr_dict

def al_report_list_to_dict(df_al):
    """
    Chuẩn hóa al_report thành dict theo employee_code:
    - Mỗi key là employee_code, value là list các bản ghi al_report tương ứng, sắp xếp giảm dần theo date_calculate_leave.
    """
    if df_al is None or df_al.empty or "employee_code" not in df_al.columns:
        return {}
    al_dict = {}
    for code, group in df_al.groupby("employee_code"):
        group_sorted = group.sort_values("date_calculate_leave", ascending=False)
        al_dict[code] = group_sorted.to_dict(orient="records")
    return al_dict

def cl_report_list_to_dict(df_cl):
    """
    Chuẩn hóa cl_report thành dict theo employee_code:
    - Mỗi key là employee_code, value là list các bản ghi cl_report tương ứng, sắp xếp giảm dần theo date_calculate.
    """
    if df_cl is None or df_cl.empty or "employee_code" not in df_cl.columns:
        return {}
    cl_dict = {}
    for code, group in df_cl.groupby("employee_code"):
        group_sorted = group.sort_values("date_calculate", ascending=False)
        cl_dict[code] = group_sorted.to_dict(orient="records")
    return cl_dict

def attendance_trans_list_to_dict(df_att):
    """
    Chuẩn hóa attendance_trans thành dict theo name:
    - Mỗi key là name, value là list các bản ghi attendance_trans tương ứng, sắp xếp giảm dần theo time.
    """
    if df_att is None or df_att.empty or "name" not in df_att.columns:
        return {}
    att_dict = {}
    for name, group in df_att.groupby("name"):
        group_sorted = group.sort_values("time", ascending=False)
        att_dict[name] = group_sorted.to_dict(orient="records")
    return att_dict

def shifts_list_to_dict(df_shifts):
    """
    Chuẩn hóa shifts thành dict 2 tầng: mis_id -> name -> list các bản ghi shifts tương ứng.
    """
    if df_shifts is None or df_shifts.empty or "mis_id" not in df_shifts.columns or "name" not in df_shifts.columns:
        return {}
    shifts_dict = {}
    for mis_id, group_mis in df_shifts.groupby("mis_id"):
        name_dict = {}
        for name, group_name in group_mis.groupby("name"):
            name_dict[name] = group_name.to_dict(orient="records")
        shifts_dict[mis_id] = name_dict
    return shifts_dict

def apec_attendance_report_list_to_dict(df_apec):
    """
    Chuẩn hóa apec_attendance_report thành dict theo employee_code:
    - Mỗi key là employee_code, value là list các bản ghi apec_attendance_report tương ứng, sắp xếp tăng dần theo date.
    """
    if df_apec is None or df_apec.empty or "employee_code" not in df_apec.columns:
        return {}
    apec_dict = {}
    for code, group in df_apec.groupby("employee_code"):
        group_sorted = group.sort_values("date", ascending=True)
        apec_dict[code] = group_sorted.to_dict(orient="records")
    return apec_dict

def contracts_list_to_dicts_by_month(df_contracts):
    """
    Trả về 3 dict:
    - contracts_dict: hợp đồng có date_start <= ngày cuối cùng tháng hiện tại
    - contracts_prev_dict: hợp đồng có date_start <= ngày cuối cùng tháng trước
    - contracts_next_dict: hợp đồng có date_start <= ngày cuối cùng tháng sau
    """
    if df_contracts is None or df_contracts.empty or "employee_code" not in df_contracts.columns or "date_start" not in df_contracts.columns:
        return {}, {}, {}
    now = datetime.now()
    # Ngày cuối cùng tháng hiện tại
    last_day_this = calendar.monthrange(now.year, now.month)[1]
    end_this = datetime(now.year, now.month, last_day_this)
    # Ngày cuối cùng tháng trước
    prev_month = now.month - 1 if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    last_day_prev = calendar.monthrange(prev_year, prev_month)[1]
    end_prev = datetime(prev_year, prev_month, last_day_prev)
    # Ngày cuối cùng tháng sau
    next_month = now.month + 1 if now.month < 12 else 1
    next_year = now.year if now.month < 12 else now.year + 1
    last_day_next = calendar.monthrange(next_year, next_month)[1]
    end_next = datetime(next_year, next_month, last_day_next)
    # Lọc hợp đồng
    contracts_dict = {}
    contracts_prev_dict = {}
    contracts_next_dict = {}
    for code, group in df_contracts.groupby("employee_code"):
        group_this = group[group["date_start"] <= end_this]
        group_prev = group[group["date_start"] <= end_prev]
        group_next = group[group["date_start"] <= end_next]
        contracts_dict[code] = group_this.sort_values("date_start").to_dict(orient="records")
        contracts_prev_dict[code] = group_prev.sort_values("date_start").to_dict(orient="records")
        contracts_next_dict[code] = group_next.sort_values("date_start").to_dict(orient="records")
    return contracts_dict, contracts_prev_dict, contracts_next_dict

def group_attendance_trans_by_shift(apec_attendance_report_dict, attendance_trans_dict, employee_dict=None):
    """
    Gom nhóm các điểm chấm công (attendance_trans_dict) vào ca làm việc dựa trên mốc thời gian (points):
    - apec_attendance_report_dict: key là employee_code, value là list các dict (attendance_report) có date, shift_start, shift_end, shift_name.
    - attendance_trans_dict: key là time_keeping_code, value là list các bản ghi (dict) có 'time' (datetime string).
    - employee_dict: key là employee_code, value là dict có key 'profiles' là list các employee dict, lấy phần tử đầu tiên để lấy 'time_keeping_code'.
    - Xử lý ca xuyên đêm: nếu shift_end < shift_start thì shift_end + 24h, ngày ca vẫn lấy theo ngày shift_start.
    - Tạo mảng points: mỗi phần tử là dict {'dt': datetime, 'date': ngày ca} gồm các mốc chia ca (midpoint giữa ca trước và ca sau).
    - Với mỗi điểm chấm công, tìm mốc point_index phù hợp để gán về ngày ca tương ứng.
    Trả về dict: key là (employee_code, ca_date, shift_name), value là list các điểm chấm công thuộc ca đó.
    """
    from collections import defaultdict
    result = defaultdict(list)
    if not apec_attendance_report_dict:
        return result
    for code, ca_list in apec_attendance_report_dict.items():
        # ca_list: list các dict có date, shift_start, shift_end, shift_name
        ca_list_sorted = sorted(ca_list, key=lambda x: pd.to_datetime(x['date']))
        ca_objs = []
        for ca in ca_list_sorted:
            ca_date = pd.to_datetime(ca['date']).date()
            s = float(ca.get('shift_start', 12.0)) if not pd.isnull(ca.get('shift_start', 12.0)) else 12.0
            e = float(ca.get('shift_end', 12.0)) if not pd.isnull(ca.get('shift_end', 12.0)) else 12.0
            if e < s:
                e += 24.0
            ca_objs.append({'date': ca_date, 'shift_start': s, 'shift_end': e, 'shift_name': ca.get('shift_name', '')})
        if not ca_objs:
            continue
        # Tạo mảng points: các mốc chia ca (midpoint giữa ca trước và ca hiện tại)
        points = []
        for i, ca in enumerate(ca_objs):
            if i == 0:
                prev_end = ca['shift_start'] - 12.0
                mid = (prev_end + ca['shift_start']) / 2.0
                dt = datetime.combine(ca['date'], datetime.min.time()) + timedelta(hours=mid)
                points.append({'dt': dt, 'date': ca['date']})
            else:
                prev = ca_objs[i-1]
                mid = (prev['shift_end'] + ca['shift_start']) / 2.0
                dt = datetime.combine(ca['date'], datetime.min.time()) + timedelta(hours=mid)
                points.append({'dt': dt, 'date': ca['date']})
        last = ca_objs[-1]
        last_mid = (last['shift_end'] + (last['shift_end'] + 12.0)) / 2.0
        dt = datetime.combine(last['date'], datetime.min.time()) + timedelta(hours=last_mid)
        points.append({'dt': dt, 'date': last['date']})
        points = sorted(points, key=lambda x: x['dt'])
        # Lấy các điểm chấm công của nhân viên này
        time_keeping_code = None
        if employee_dict and code in employee_dict and employee_dict[code]:
            emp_list = employee_dict[code].get('profiles', [])
            if emp_list:
                emp = emp_list[0]
                time_keeping_code = emp.get('time_keeping_code')
        punch_list = []
        if time_keeping_code and time_keeping_code in attendance_trans_dict:
            punch_list = attendance_trans_dict[time_keeping_code]
        elif code in attendance_trans_dict:
            punch_list = attendance_trans_dict[code]
        punch_list = sorted(punch_list, key=lambda x: pd.to_datetime(x['time']))
        point_index = 0
        for punch in punch_list:
            punch_dt = pd.to_datetime(punch['time'])
            while point_index < len(points)-1 and punch_dt >= points[point_index+1]['dt']:
                point_index += 1
            ca_date = points[point_index]['date']
            ca_info = next((c for c in ca_objs if c['date'] == ca_date), None)
            shift_name = ca_info['shift_name'] if ca_info else ''
            punch['date_by_shift'] = ca_date
            punch['code'] = code
            result[(code, ca_date, shift_name)].append(punch)
    return dict(result)
