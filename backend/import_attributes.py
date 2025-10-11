#!/usr/bin/env python3
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.producttemplates.models import AttributeGroup, AttributeSubGroup, Attribute
from django.contrib.auth import get_user_model

User = get_user_model()

# Đường dẫn file excel (chỉnh nếu cần)
EXCEL_PATH = os.path.join('data', 'Template for Product Hierarchy & Product Master with Attributes.xlsx')

# Hàng bắt đầu chứa các giá trị Value (0-index). Chỉnh nếu file khác.
VALUES_START_ROW = 5

def _clean_cell(cell):
    """
    Chuẩn hóa ô:
    - NaN -> ''
    - số 0 hoặc '0' -> ''
    - chuỗi 'nan' -> ''
    - else -> stripped string
    """
    if pd.isna(cell):
        return ''
    if isinstance(cell, (int, float)) and cell == 0:
        return ''
    s = str(cell).strip()
    if s == '' or s.lower() == 'nan' or s == '0':
        return ''
    return s

def import_attributes():
    # Đọc sheet 'Product Master', header=None để giữ cấu trúc file gốc
    df = pd.read_excel(EXCEL_PATH, sheet_name='Product Master', header=None)

    # Chuẩn bị hàng header (row index 2,3,4 tương ứng Group, SubGroup, Attribute)
    # Forward-fill (ffill) trên hàng Group và SubGroup để xử lý merged headers
    nrows, ncols = df.shape
    if nrows <= 4:
        raise RuntimeError("File quá ít hàng; cần tối thiểu 5 hàng để chứa group/subgroup/attribute/values")

    # Lấy toàn bộ hàng header rồi ffill, sau đó lấy phần cột từ index 1 trở đi (giữ như logic gốc)
    groups_row = df.iloc[2, :].copy().apply(lambda x: x if (not pd.isna(x) and str(x).strip() != '') else pd.NA).ffill()
    subgroups_row = df.iloc[3, :].copy().apply(lambda x: x if (not pd.isna(x) and str(x).strip() != '') else pd.NA).ffill()
    attributes_row = df.iloc[4, :].copy()  # attribute thường không ffill (nếu attribute bị merge thì vẫn là design issue)

    # Lặp qua các cột thực tế: dùng df.columns[1:] để tránh lệ thuộc range()
    for col in df.columns[1:]:
        # Lấy và clean header từ hàng đã ffill
        raw_group = _clean_cell(groups_row.get(col, ''))
        raw_subgroup = _clean_cell(subgroups_row.get(col, ''))
        attribute_name = _clean_cell(attributes_row.get(col, ''))

        # Quy tắc:
        # - nếu group trống -> group='General', subgroup='General'
        # - nếu group có nhưng subgroup trống -> subgroup = group
        if not raw_group:
            group_name = 'General'
            subgroup_name = 'General'
        else:
            group_name = raw_group
            subgroup_name = raw_subgroup if raw_subgroup else group_name

        # Bỏ qua CHỈ khi attribute trống (để không mất BOM, Cost of goods,...)
        if not attribute_name:
            print(f"Col {col}: skipped because attribute empty -> group='{group_name}', subgroup='{subgroup_name}'")
            continue

        # Thu thập giá trị theo chiều dọc trong cột này (từ VALUES_START_ROW xuống)
        values = []
        for r in range(VALUES_START_ROW, nrows):
            try:
                v = _clean_cell(df.iat[r, col])
            except Exception:
                v = ''
            if v:
                values.append(v)

        # Nếu không có giá trị dọc, dò ngang các cột kế tiếp (value trải ngang)
        if not values:
            c_idx = list(df.columns).index(col) + 1
            while c_idx < len(df.columns):
                c = df.columns[c_idx]
                # nếu cột c có header (group/subgroup/attribute) thì dừng vì đó là attribute tiếp theo
                g = _clean_cell(groups_row.get(c, '')) if 2 < nrows else ''
                sg = _clean_cell(subgroups_row.get(c, '')) if 3 < nrows else ''
                at = _clean_cell(attributes_row.get(c, '')) if 4 < nrows else ''
                if g or sg or at:
                    break
                # ngược lại thu thập giá trị ở cột c
                for r in range(VALUES_START_ROW, nrows):
                    try:
                        v = _clean_cell(df.iat[r, c])
                    except Exception:
                        v = ''
                    if v:
                        values.append(v)
                c_idx += 1

        # Đảm bảo values là list (nếu không có => [])
        info = {"value": values}

        # Tạo / cập nhật record trong DB (giữ logic get_or_create như cũ)
        group_obj, _ = AttributeGroup.objects.get_or_create(
            name=group_name,
            defaults={
                'display_name': group_name,
                'description': '',
            }
        )

        subgroup_obj, _ = AttributeSubGroup.objects.get_or_create(
            group=group_obj,
            name=subgroup_name,
            defaults={
                'display_name': subgroup_name,
                'sequence': int(col),
                'description': '',
            }
        )

        attr_defaults = {
            'display_name': attribute_name,
            'code_mch': '',
            'sequence': int(col),
            'info': info,
        }

        attribute_obj, created = Attribute.objects.get_or_create(
            subgroup=subgroup_obj,
            name=attribute_name,
            defaults=attr_defaults
        )

        if created:
            print(f"Col {col}: CREATED attribute '{attribute_name}' (Group: '{group_name}' / SubGroup: '{subgroup_name}') values={values}")
        else:
            # Nếu đã tồn tại, cập nhật info, sequence, display_name
            attribute_obj.info = info
            attribute_obj.sequence = int(col)
            attribute_obj.display_name = attribute_name
            attribute_obj.save()
            print(f"Col {col}: UPDATED attribute '{attribute_name}' (Group: '{group_name}' / SubGroup: '{subgroup_name}') values={values}")

if __name__ == '__main__':
    import_attributes()
    print('Import completed.')
