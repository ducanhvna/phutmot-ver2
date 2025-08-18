# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BTMHDatCoc(models.Model):
    """Model chứa dữ liệu đặt cọc từ BTMH POS"""
    _name = 'btmh.dat_coc'
    _description = 'BTMH - Dat Coc Thanh Toan'
    _order = 'ngay_dat desc, id_dat_coc'
    _rec_name = 'display_name'
    
    # Thông tin chính từ SlVbDCD
    id_dat_coc = fields.Char('ID Đặt Cọc BTMH', required=True, index=True, help="SlVbDCD.ID")
    
    # Thông tin kho và sản phẩm
    ma_kho = fields.Char('Mã Kho', help="DmKho.Ma_Kho")
    ma_hang = fields.Char('Mã Hàng', required=True, index=True, help="DmH.Ma_Hang")
    ten_hang = fields.Char('Tên Hàng', required=True, help="fTCVNToUnicode(DmH.Ten_Hang)")
    ma_mau = fields.Char('Mã Mẫu', help="RTRIM(DmH.Ma_Tong)")
    
    # Mã chung sản phẩm - logic phức tạp từ SQL
    ma_chung_sp = fields.Char('Mã Chung SP', help="Logic phân loại theo Ma_Hang")
    
    # Thông tin số lượng và giá
    so_luong = fields.Float('Số Lượng', digits=(16, 6), help="SlVbDCD.So_Luong")
    ty_gia = fields.Float('Tỷ Giá', digits=(16, 2), help="SlVbDCD.Ty_Gia")  
    tong_tien = fields.Monetary('Tổng Tiền', currency_field='currency_id', help="SlVbDCD.Tong_Tien")
    
    # Thông tin khách hàng - với dấu *
    ma_khach = fields.Char('Mã Khách', index=True, help="Với dấu * - DmDt.Ma_Dt")
    ten_khach = fields.Char('Tên Khách', help="fTCVNToUnicode(DmDt.Ten_Dt)")
    dia_chi = fields.Text('Địa Chỉ', help="fTCVNToUnicode(DmDt.Dia_Chi)")
    dien_thoai = fields.Char('Điện Thoại', help="Với dấu * - DmDt.Dien_Thoai")
    cccd_cmnd = fields.Char('CCCD/CMND', help="Với dấu * - DmDt.So_CMT")
    
    # Thông tin ngày tháng
    ngay_dat = fields.Date('Ngày Đặt', required=True, help="FORMAT(SlVbDcM.Ngay,'yyyy-MM-dd')")
    ngay_giao = fields.Date('Ngày Giao', help="FORMAT(SlVbDcM.Ngay_Giao,'yyyy-MM-dd')")
    dien_giai = fields.Text('Diễn Giải', help="fTCVNToUnicode(SlVbDcM.Dien_Giai)")
    
    # Thông tin đại chỉ và liên kết
    id_dai_chi = fields.Char('ID Đại Chỉ', help="DmH.Ten_HangN")
    sub_id = fields.Char('Sub ID', help="SlBlM.Sub_ID")
    
    # Trạng thái đặt cọc
    trang_thai_coc = fields.Selection([
        ('da_thanh_toan_coc', 'Đã Thanh Toán Cọc'),      # IsCopy=1
        ('chua_ket_coc', 'Chưa Kết Cọc'),               # SlBlM.Sub_ID is NULL
        ('da_ket_coc', 'Đã Kết Cọc'),                   # SlBlM.Sub_ID is not NULL
        ('huy', 'Hủy')
    ], string='Trạng Thái Cọc', default='da_thanh_toan_coc', index=True)
    
    # Điều kiện lọc sản phẩm tích trữ
    la_san_pham_tich_tru = fields.Boolean('Là SP Tích Trữ', default=True, 
        help="Chi lay nhom tich tru: KGB%, TTSJV24KD0%, KHS%, TTV%, NLMVV49KD0%, hoặc các mã đặc biệt")
    
    # Trạng thái sync
    trang_thai_sync = fields.Selection([
        ('chua_sync', 'Chưa Sync'),
        ('dang_sync', 'Đang Sync'),
        ('da_sync', 'Đã Sync'), 
        ('loi', 'Lỗi')
    ], string='Trạng Thái Sync', default='chua_sync', index=True)
    
    ngay_sync = fields.Datetime('Ngày Sync')
    loi_sync = fields.Text('Lỗi Sync')
    
    # Liên kết Odoo
    deposit_order_id = fields.Many2one('sale.order', 'Đơn Hàng Cọc Odoo', ondelete='set null')
    partner_id = fields.Many2one('res.partner', 'Khách Hàng Odoo', ondelete='set null')
    product_id = fields.Many2one('product.product', 'Sản Phẩm Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('id_dat_coc', 'ma_hang', 'ten_khach', 'ngay_dat')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.id_dat_coc} - {record.ma_hang} - {record.ten_khach} - {record.ngay_dat}"
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'id_dat_coc': btmh_data.get('ID'),
                'ma_kho': btmh_data.get('Ma_Kho'),
                'ma_hang': btmh_data.get('Ma_Hang'),
                'ten_hang': btmh_data.get('Ten_Hang'),
                'ma_mau': btmh_data.get('Ma mau'),
                'ma_chung_sp': btmh_data.get('Ma_Chung_SP'),
                'so_luong': float(btmh_data.get('So_Luong', 0)),
                'ty_gia': float(btmh_data.get('Ty_Gia', 0)),
                'tong_tien': float(btmh_data.get('Tong_Tien', 0)),
                'ma_khach': btmh_data.get('Ma_Khach'),        # Đã có dấu *
                'ten_khach': btmh_data.get('Ten_Khach'),
                'dia_chi': btmh_data.get('Dia_Chi'),
                'dien_thoai': btmh_data.get('Dien_Thoai'),    # Đã có dấu *
                'cccd_cmnd': btmh_data.get('CCCD\\CMND'),     # Đã có dấu *
                'ngay_dat': self._parse_date(btmh_data.get('Ngay_Dat')),
                'ngay_giao': self._parse_date(btmh_data.get('Ngay_Giao')),
                'dien_giai': btmh_data.get('Dien_Giai'),
                'id_dai_chi': btmh_data.get('ID_DaiChi'),
                'sub_id': btmh_data.get('Sub_ID'),
                'trang_thai_coc': 'chua_ket_coc' if not btmh_data.get('Sub_ID') else 'da_ket_coc',
                'la_san_pham_tich_tru': self._check_san_pham_tich_tru(btmh_data.get('Ma_Hang')),
                'trang_thai_sync': 'chua_sync'
            }
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Lỗi tạo đặt cọc từ BTMH data: {str(e)}")
            raise UserError(f"Không thể tạo đặt cọc: {str(e)}")
    
    def _parse_date(self, date_str):
        """Parse date string yyyy-MM-dd"""
        if not date_str:
            return False
        try:
            return fields.Date.from_string(date_str)
        except:
            return False
    
    def _check_san_pham_tich_tru(self, ma_hang):
        """Kiểm tra có phải sản phẩm tích trữ không"""
        if not ma_hang:
            return False
            
        # Danh sách pattern từ SQL WHERE clause
        tich_tru_patterns = [
            'KGB%', 'TTSJV24KD0%', 'KHS%', 'TTV%', 'NLMVV49KD0%'
        ]
        
        # Danh sách mã đặc biệt
        ma_dac_biet = [
            'NLKGV24KD0-208001-001', 'NLNLV0KKD0-401001-0001', 'NL9999', 
            'NL9999KD', 'NLKGB', 'NL06', 'NL999', 'NL999KD', 'NLSJC', 'NLVRTL', 'NLVVTA'
        ]
        
        # Kiểm tra pattern với LIKE
        for pattern in tich_tru_patterns:
            if ma_hang.startswith(pattern.replace('%', '')):
                return True
                
        # Kiểm tra mã đặc biệt
        return ma_hang in ma_dac_biet
    
    @api.model  
    def sync_from_btmh_database(self):
        """Sync dữ liệu từ BTMH database"""
        # Implementation để connect và pull data từ SQL Server
        # WHERE SlVbDcM.ID_Dv=0 AND SlVbDcM.IsCopy=1 AND SlBlM.Sub_ID is NULL
        pass
    
    def action_ket_coc(self):
        """Action kết cọc - tạo đơn hàng thật"""
        for record in self:
            if record.trang_thai_coc != 'chua_ket_coc':
                raise UserError("Chỉ có thể kết cọc cho đơn chưa kết cọc!")
            
            # Logic tạo sale order từ đặt cọc
            # Tạo customer, product nếu chưa có
            # ...
            
            record.trang_thai_coc = 'da_ket_coc'
    
    # Thông tin đặt cọc
    id_dat_coc = fields.Char('ID Đặt Cọc', required=True, index=True)
    ma_kho = fields.Char('Mã Kho')
    
    # Thông tin sản phẩm
    ma_hang = fields.Char('Mã Hàng', required=True, index=True)
    ten_hang = fields.Char('Tên Hàng', required=True)
    ma_mau = fields.Char('Mã Mẫu')
    ma_chung_sp = fields.Char('Mã Chung SP')  # Mã nhóm sản phẩm chung
    
    # Thông tin số lượng và giá
    so_luong = fields.Float('Số Lượng', digits=(16, 6))
    ty_gia = fields.Float('Tỷ Giá', digits=(16, 2))
    tong_tien = fields.Monetary('Tổng Tiền', currency_field='currency_id')
    
    # Thông tin khách hàng
    ma_khach = fields.Char('Mã Khách', index=True)
    ten_khach = fields.Char('Tên Khách')
    dia_chi = fields.Text('Địa Chỉ')
    dien_thoai = fields.Char('Điện Thoại')
    cccd_cmnd = fields.Char('CCCD/CMND')
    
    # Thông tin thời gian
    ngay_dat = fields.Date('Ngày Đặt', required=True, index=True)
    ngay_giao = fields.Date('Ngày Giao')
    dien_giai = fields.Text('Diễn Giải')
    
    # Thông tin hệ thống  
    id_dai_chi = fields.Char('ID Đại Chỉ')
    sub_id = fields.Char('Sub ID')
    
    # Trạng thái đặt cọc
    trang_thai_dat_coc = fields.Selection([
        ('da_coc', 'Đã Cọc'),
        ('chua_nhan_hang', 'Chưa Nhận Hàng'),
        ('da_nhan_hang', 'Đã Nhận Hàng'),
        ('huy', 'Hủy')
    ], string='Trạng Thái Đặt Cọc', default='da_coc')
    
    # Sync information
    trang_thai_sync = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_sync', 'Chờ Sync'),
        ('da_sync', 'Đã Sync'),
        ('loi', 'Lỗi')
    ], string='Trạng Thái Sync', default='nhap', index=True)
    
    ngay_sync = fields.Datetime('Ngày Sync')
    loi_sync = fields.Text('Lỗi Sync')
    
    # Liên kết với Odoo
    don_hang_ban_odoo_id = fields.Many2one('sale.order', 'Đơn Hàng Bán Odoo', ondelete='set null')
    khach_hang_odoo_id = fields.Many2one('res.partner', 'Khách Hàng Odoo', ondelete='set null')
    san_pham_odoo_id = fields.Many2one('product.product', 'Sản Phẩm Odoo', ondelete='set null')
    hoa_don_tam_ung_odoo_id = fields.Many2one('account.move', 'Hóa Đơn Tạm Ứng Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ', 
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('id_dat_coc', 'ten_khach', 'ma_hang')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.id_dat_coc} - {record.ten_khach} - {record.ma_hang}"
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'id_dat_coc': str(btmh_data.get('ID')),
                'ma_kho': btmh_data.get('Ma_Kho'),
                'ma_hang': btmh_data.get('Ma_Hang'),
                'ten_hang': btmh_data.get('Ten_Hang'),
                'ma_mau': btmh_data.get('Ma mau'),
                'ma_chung_sp': btmh_data.get('Ma_Chung_SP'),
                'so_luong': float(btmh_data.get('So_Luong', 0)),
                'ty_gia': float(btmh_data.get('Ty_Gia', 0)),
                'tong_tien': float(btmh_data.get('Tong_Tien', 0)),
                'ma_khach': btmh_data.get('Ma_Khach', '').replace('*', ''),
                'ten_khach': btmh_data.get('Ten_Khach'),
                'dia_chi': btmh_data.get('Dia_Chi'),
                'dien_thoai': btmh_data.get('Dien_Thoai', '').replace('*', ''),
                'cccd_cmnd': btmh_data.get('CCCD\CMND', '').replace('*', ''),
                'dien_giai': btmh_data.get('Dien_Giai'),
                'id_dai_chi': btmh_data.get('ID_DaiChi'),
                'sub_id': btmh_data.get('Sub_ID'),
                'trang_thai_sync': 'cho_sync'
            }
            
            # Parse ngày đặt
            ngay_dat = btmh_data.get('Ngay_Dat')
            if ngay_dat:
                vals['ngay_dat'] = fields.Date.from_string(ngay_dat)
            
            # Parse ngày giao
            ngay_giao = btmh_data.get('Ngay_Giao')
            if ngay_giao:
                vals['ngay_giao'] = fields.Date.from_string(ngay_giao)
            
            # Xác định trạng thái
            if btmh_data.get('Sub_ID'):  # Đã nhận hàng
                vals['trang_thai_dat_coc'] = 'da_nhan_hang'
            else:  # Chưa nhận hàng
                vals['trang_thai_dat_coc'] = 'chua_nhan_hang'
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating BTMH deposit data: {e}")
            raise UserError(f"Lỗi tạo dữ liệu đặt cọc: {e}")
    
    def action_sync_to_odoo(self):
        """Đồng bộ lên Odoo ERP"""
        for record in self:
            try:
                record.trang_thai_sync = 'cho_sync'
                
                # Tạo hoặc tìm khách hàng
                partner = record._get_or_create_partner()
                record.khach_hang_odoo_id = partner.id
                
                # Tạo hoặc tìm sản phẩm
                product = record._get_or_create_product()
                record.san_pham_odoo_id = product.id
                
                # Tạo đơn hàng bán (sale order)
                sale_order = record._create_sale_order(partner, product)
                record.don_hang_ban_odoo_id = sale_order.id
                
                # Tạo hóa đơn tạm ứng nếu có tiền cọc
                if record.tong_tien > 0:
                    down_payment_invoice = record._create_down_payment_invoice(sale_order)
                    record.hoa_don_tam_ung_odoo_id = down_payment_invoice.id
                
                record.trang_thai_sync = 'da_sync'
                record.ngay_sync = fields.Datetime.now()
                record.loi_sync = False
                
                # Ghi log
                self.env['btmh.sync.log'].create({
                    'ten_model': 'btmh.dat_coc',
                    'id_ban_ghi': record.id,
                    'loai_sync': 'manual',
                    'trang_thai': 'thanh_cong',
                    'thong_bao': f'Đồng bộ thành công đặt cọc {record.id_dat_coc}'
                })
                
            except Exception as e:
                record.trang_thai_sync = 'loi'
                record.loi_sync = str(e)
                _logger.error(f"Error syncing record {record.id}: {e}")
    
    def _get_or_create_partner(self):
        """Tạo hoặc tìm khách hàng"""
        if not self.ma_khach:
            # Tạo partner với tên khách hàng
            return self.env['res.partner'].create({
                'name': self.ten_khach or 'Khách lẻ',
                'phone': self.dien_thoai,
                'street': self.dia_chi,
                'is_company': False,
                'customer_rank': 1
            })
        
        partner = self.env['res.partner'].search([
            ('ref', '=', self.ma_khach)
        ], limit=1)
        
        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.ten_khach or self.ma_khach,
                'ref': self.ma_khach,
                'phone': self.dien_thoai,
                'street': self.dia_chi,
                'is_company': False,
                'customer_rank': 1
            })
        
        return partner
    
    def _get_or_create_product(self):
        """Tạo hoặc tìm sản phẩm"""
        product = self.env['product.product'].search([
            ('default_code', '=', self.ma_hang)
        ], limit=1)
        
        if not product:
            # Tính giá bán từ tổng tiền / số lượng
            unit_price = self.tong_tien / self.so_luong if self.so_luong > 0 else 0
            
            product = self.env['product.product'].create({
                'name': self.ten_hang or self.ma_hang,
                'default_code': self.ma_hang,
                'type': 'product',
                'list_price': unit_price,
                'standard_price': unit_price * 0.8,  # Cost price
                'sale_ok': True,
                'purchase_ok': True
            })
        
        return product
    
    def _create_sale_order(self, partner, product):
        """Tạo đơn hàng bán"""
        # Tính giá đơn vị
        unit_price = self.tong_tien / self.so_luong if self.so_luong > 0 else 0
        
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': self.ngay_dat,
            'validity_date': self.ngay_giao,
            'origin': f'BTMH-COC-{self.id_dat_coc}',
            'note': self.dien_giai,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': self.ten_hang,
                'product_uom_qty': self.so_luong,
                'price_unit': unit_price,
            })]
        })
        
        # Xác nhận đơn hàng
        sale_order.action_confirm()
        
        return sale_order
    
    def _create_down_payment_invoice(self, sale_order):
        """Tạo hóa đơn tạm ứng (down payment)"""
        # Tạo down payment wizard
        down_payment_wizard = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'fixed',
            'fixed_amount': self.tong_tien,
            'deposit_account_id': self.env['account.account'].search([
                ('code', 'like', '3311')  # Tài khoản người mua trả tiền trước
            ], limit=1).id
        })
        
        # Create down payment invoice
        result = down_payment_wizard.with_context(active_ids=sale_order.ids).create_invoices()
        
        # Tìm invoice vừa tạo
        invoice = self.env['account.move'].browse(result.get('res_id'))
        
        # Confirm invoice
        if invoice:
            invoice.action_post()
        
        return invoice
