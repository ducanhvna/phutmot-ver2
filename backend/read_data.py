import os
import pandas as pd
from datetime import datetime
import django

# Khởi tạo môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Đổi 'yourproject' thành tên project của Anh
django.setup()


# Sau khi setup, có thể import model
from apps.customers.models import Customer

# Đọc đơn hàng
df_orders = pd.read_parquet('data/DuLieuDumpDonHang.parquet')

# Đọc tất cả file khách hàng
customer_dir = 'data/DumpDataCustomer'
customer_files = [os.path.join(customer_dir, f) for f in os.listdir(customer_dir) if f.endswith('.parquet')]
df_customers = pd.concat([pd.read_parquet(f) for f in customer_files], ignore_index=True)

# Lặp qua từng dòng khách hàng để tạo Customer object
for _, row in df_customers.iterrows():
    try:
        customer_id = str(row['Ma_Dt']).strip()
        phone = str(row['Dien_Thoai']).strip() if pd.notna(row['Dien_Thoai']) else None
        birth_date = pd.to_datetime(row['Ngay_Sinh'], errors='coerce').date() if pd.notna(row['Ngay_Sinh']) else None
        gender = 'Female' if str(row['Gioi_Tinh']).strip() == 'N÷' else 'Male'
        email = str(row['Email']).strip() if pd.notna(row['Email']) else None
        # Gom các thông tin địa chỉ vào một dict
        def safe_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        address = {
            'full': str(row['Dia_Chi']).strip() if pd.notna(row['Dia_Chi']) else None,
            'ward_id': safe_int(row['ID_Phuong']) if pd.notna(row['ID_Phuong']) else None,
            'district_id': safe_int(row['ID_Quan']) if pd.notna(row['ID_Quan']) else None,
            'province_id': safe_int(row['ID_Tinh']) if pd.notna(row['ID_Tinh']) else None,
            'id_card_issue_place': str(row['NoiC_CMT']).strip() if pd.notna(row['NoiC_CMT']) else None,
            'id_card_issue_date': str(pd.to_datetime(row['NgayC_CMT'], errors='coerce').date()) if pd.notna(row['NgayC_CMT']) else None
        }

        # Lấy đơn hàng liên quan
        orders = df_orders[df_orders['ID_Dt'] == row['ID']].copy()
        order_list = []
        for _, o in orders.iterrows():
            order_list.append({
                'order_code': o['So_Ct'],
                'date': str(o['Ngay']),
                'salesperson': o['Dien_Giai'],
                'amount': float(o['Tien_Hang']),
                'invoice_url': o['WLink'] if pd.notna(o['WLink']) else None
            })

        # Tạo hoặc cập nhật Customer
        customer, created = Customer.objects.update_or_create(
            id_card_number=str(row['So_CMT']).strip(),
            defaults={
                'username': customer_id,
                'phone_number': phone,
                'old_id_card_number': str(row['So_CMT']).strip(),
                'name': str(row['Ten_Dt']).strip(),
                'english_name': str(row['Ten_DtE']).strip() if pd.notna(row['Ten_DtE']) else None,
                'gender': gender,
                'birth_date': birth_date,
                'email': email,
                'address': address,
                'info': {
                    'store_type': int(row['LoaiDt']) if pd.notna(row['LoaiDt']) else None,
                    'store_notes': str(row['Ghi_Chu']).strip() if pd.notna(row['Ghi_Chu']) else None,
                    'is_active': not bool(row['Inactive']),
                    'created_at': str(row['InsertDate']),
                    'last_updated': str(row['LastEdit']),
                    'orders': order_list
                }
            }
        )
        print(f"{'Created' if created else 'Updated'} customer: {customer.username}")
    except Exception as e:
        print(f"❌ Error importing customer {row.get('Ma_Dt')}: {e}")
