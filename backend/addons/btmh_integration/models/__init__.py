# -*- coding: utf-8 -*-

# Import models cũ (sẽ tạm thời giữ lại để tránh lỗi migration)
from . import btmh_sales_data
from . import btmh_payment_data  
from . import btmh_deposit_data
from . import btmh_sync_log
from . import btmh_fabric_pipeline

# Import models mới với tên tiếng Việt
from . import btmh_doanh_thu_ban_hang
from . import btmh_chung_tu_thanh_toan
from . import btmh_dat_coc
from . import btmh_du_dau_ngay
from . import btmh_nhat_ky_dong_bo
from . import res_partner
from . import account_move
