import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.utils.transform_helpers import (
    transform_apec_attendance_report,
    process_report_raw,
    find_couple_row,
    find_couple_out_in_row,
    calculate_actual_work_time_couple_for_out_in,
    get_scheduling_time_row,
)
import pandas as pd
from datetime import datetime

def test_process_report_raw_basic():
    row = {
        'date': datetime(2024, 5, 1),
        'start_work_time': 8.0,
        'end_work_time': 17.0,
        'start_rest_time': 12.0,
        'end_rest_time': 13.0,
        'shift_start': 8.0,
        'shift_end': 17.0,
        'rest_start': 12.0,
        'rest_end': 13.0,
    }
    shift_start, shift_end, rest_start, rest_end = process_report_raw(row)
    assert shift_start.hour == 8
    assert shift_end.hour == 17
    assert rest_start.hour == 12
    assert rest_end.hour == 13

def test_process_report_raw_cross_day():
    row = {
        'date': datetime(2024, 5, 1),
        'start_work_time': 22.0,
        'end_work_time': 6.0,
        'start_rest_time': 2.0,
        'end_rest_time': 3.0,
        'shift_start': 22.0,
        'shift_end': 6.0,
        'rest_start': 2.0,
        'rest_end': 3.0
    }
    sdt, edt, rsdt, redt = process_report_raw(row)
    assert sdt.hour == 22
    assert edt.hour == 6 and edt.day == 2  # sang ngày hôm sau
    assert rsdt.hour == 2 and rsdt.day == 2
    assert redt.hour == 3 and redt.day == 2
    assert edt > sdt
    assert redt > rsdt

def test_find_couple_row_basic():
    row = {f'attendance_inout_{i}': 'I' if i % 2 == 1 else 'O' for i in range(1, 5)}
    row.update({f'attendance_attempt_{i}': datetime(2024, 5, 1, 8 + i) for i in range(1, 5)})
    couples = find_couple_row(row)
    assert couples == [[(1, 2), (3, 4)]]

def test_find_couple_out_in_row_basic():
    row = {f'attendance_inout_{i}': 'O' if i % 2 == 1 else 'I' for i in range(1, 5)}
    row.update({f'attendance_attempt_{i}': datetime(2024, 5, 1, 8 + i) for i in range(1, 5)})
    row['shift_start_datetime'] = datetime(2024, 5, 1, 8)
    row['shift_end_datetime'] = datetime(2024, 5, 1, 17)
    row['rest_start_datetime'] = datetime(2024, 5, 1, 12)
    row['rest_end_datetime'] = datetime(2024, 5, 1, 13)
    row['fix_rest_time'] = False
    result, total = find_couple_out_in_row(row)
    assert result == [[(1, 2), (3, 4)]]
    assert isinstance(total, int)

def test_calculate_actual_work_time_couple_for_out_in_basic():
    row = {
        'shift_start_datetime': datetime(2024, 5, 1, 8),
        'shift_end_datetime': datetime(2024, 5, 1, 17),
        'rest_start_datetime': datetime(2024, 5, 1, 12),
        'rest_end_datetime': datetime(2024, 5, 1, 13),
        'fix_rest_time': False,
    }
    real_time_in = datetime(2024, 5, 1, 9)
    real_time_out = datetime(2024, 5, 1, 11)
    result = calculate_actual_work_time_couple_for_out_in(row, real_time_in, real_time_out)
    assert result['total_work_time'] >= 0

def test_transform_apec_attendance_report_basic():
    df = pd.DataFrame([
        {
            'date': datetime(2024, 5, 1),
            'start_work_time': 8.0,
            'end_work_time': 17.0,
            'start_rest_time': 12.0,
            'end_rest_time': 13.0,
            'shift_start': 8.0,
            'shift_end': 17.0,
            'rest_start': 12.0,
            'rest_end': 13.0,
            'id': 1,
            'shift_name': 'A',
            'rest_shift': False,
            'total_shift_work_time': 480,
            'fix_rest_time': False,
            'time_keeping_code': 'EMP001',
            'date_str': '2024-05-01',
            **{f'attendance_inout_{i}': 'I' if i % 2 == 1 else 'O' for i in range(1, 5)},
            **{f'attendance_attempt_{i}': datetime(2024, 5, 1, 8 + i) for i in range(1, 5)},
        }
    ])
    df2 = transform_apec_attendance_report(df)
    assert 'shift_start_datetime' in df2.columns
    assert 'couple' in df2.columns
    assert 'couple_out_in' in df2.columns
    assert 'total_out_ho' in df2.columns

def test_get_scheduling_time_row_basic():
    df_old = pd.DataFrame([
        {'Ngày': '2024-05-01', 'time_keeping_code': 'EMP001', 'Giờ': datetime(2024, 5, 1, 8), 'in_out': 'I'},
        {'Ngày': '2024-05-01', 'time_keeping_code': 'EMP001', 'Giờ': datetime(2024, 5, 1, 12), 'in_out': 'O'},
    ])
    row = {
        'date_str': '2024-05-01',
        'time_keeping_code': 'EMP001',
        'fix_rest_time': False,
        'id': 1,
        'shift_name': 'A',
        'rest_shift': False,
        'total_shift_work_time': 480,
        'shift_start_datetime': datetime(2024, 5, 1, 8),
        'shift_end_datetime': datetime(2024, 5, 1, 17),
        'rest_start_datetime': datetime(2024, 5, 1, 12),
        'rest_end_datetime': datetime(2024, 5, 1, 13),
    }
    has_attendance, min_time_out, max_time_in = get_scheduling_time_row(row, df_old)
    assert has_attendance is False
