def add_name_field(data_list, id_field='company_id'):
    """
    Bổ sung trường *_name cho mỗi dict trong data_list dựa vào id_field dạng [id, name].
    Nếu không có hoặc lỗi, gán False.
    id_field: tên trường id (vd: company_id, department_id, ...)
    name_field sẽ tự động là id_field thay '_id' cuối cùng bằng '_name'.
    """
    if not id_field.endswith('_id'):
        raise ValueError('id_field phải kết thúc bằng _id')
    name_field = id_field[:-3] + '_name'
    for item in data_list:
        try:
            name_value = item[id_field][1]
            item[name_field] = name_value
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
