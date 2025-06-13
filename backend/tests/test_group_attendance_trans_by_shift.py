import json
import os
import pytest
from app.utils.transform_helpers import group_attendance_trans_by_shift

test_dir = os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def sample_data():
    with open(os.path.join(test_dir, '1__apec_attendance_report_dict.json'), encoding='utf-8') as f:
        apec_attendance_report_dict = json.load(f)
    with open(os.path.join(test_dir, '1__attendance_trans_dict.json'), encoding='utf-8') as f:
        attendance_trans_dict = json.load(f)
    with open(os.path.join(test_dir, '1__employees_dict.json'), encoding='utf-8') as f:
        employees_dict = json.load(f)
    return apec_attendance_report_dict, attendance_trans_dict, employees_dict

def test_group_attendance_trans_by_shift_basic(sample_data):
    apec_attendance_report_dict, attendance_trans_dict, employees_dict = sample_data
    result = group_attendance_trans_by_shift(
        apec_attendance_report_dict,
        attendance_trans_dict,
        employees_dict
    )
    # Kiểm tra kết quả là dict và có key đúng định dạng
    assert isinstance(result, dict)
    for k, v in result.items():
        assert isinstance(k, tuple)
        assert len(k) == 3
        assert isinstance(v, list)
        # Kiểm tra mỗi punch có trường date_by_shift và code
        for punch in v:
            assert 'date_by_shift' in punch
            assert 'code' in punch
    # Có thể kiểm tra thêm số lượng nhóm, số lượng punch, ... nếu muốn
