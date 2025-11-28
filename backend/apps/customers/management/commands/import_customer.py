import sqlite3
from datetime import datetime
from django.core.management.base import BaseCommand
from apps.customers.models import Customer

class Command(BaseCommand):
    help = "Import dữ liệu Customer từ file SQLite theo batch (update nếu tồn tại, tạo mới nếu chưa)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--sqlite_file',
            type=str,
            required=True,
            help='Đường dẫn tới file SQLite nguồn'
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=100,
            help='Số lượng bản ghi mỗi batch'
        )

    def handle(self, *args, **options):
        sqlite_file = options['sqlite_file']
        batch_size = options['batch_size']

        # Kết nối SQLite
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        cursor.execute("SELECT ma_kh, ten_kh, dia_chi, dien_thoai, ngay_sinh, gioi_tinh, tinh, quan, phuong,ngay_tao, ngay_sua, cccd FROM customers")
        rows = cursor.fetchall()
        conn.close()

        self.stdout.write(self.style.SUCCESS(f"Tổng số bản ghi: {len(rows)}"))

        for i, row in enumerate(rows, start=1):
            ma_kh, ten_kh, dia_chi, dien_thoai, ngay_sinh, gioi_tinh, tinh, quan, phuong,ngay_tao, ngay_sua, cccd = row
            if not ma_kh:
                continue  # bỏ qua bản ghi không có số CCCD

            # Chuyển đổi ngày sinh sang dạng date
            birth_date = None
            if ngay_sinh:
                try:
                    birth_date = datetime.strptime(ngay_sinh, "%Y-%m-%d").date()
                except ValueError:
                    pass

            # Map giới tính
            gender = None
            if gioi_tinh:
                if gioi_tinh.lower() in ["nam", "male"]:
                    gender = "Male"
                elif gioi_tinh.lower() in ["nữ", "female"]:
                    gender = "Female"

            # Update nếu tồn tại, tạo mới nếu chưa
            Customer.objects.update_or_create(
                username=ma_kh,   # điều kiện tìm
                defaults={
                    "name": ten_kh,
                    "address": {"full": dia_chi} if dia_chi else None,
                    "phone_number": dien_thoai,
                    "birth_date": birth_date,
                    "gender": gender,
                    "id_card_number": cccd,
                    "is_active": True,
                    "verification_status": False
                }
            )

            if i % batch_size == 0:
                self.stdout.write(self.style.SUCCESS(f"Đã xử lý {i} bản ghi..."))

        self.stdout.write(self.style.SUCCESS("Đã import xong toàn bộ dữ liệu!"))
