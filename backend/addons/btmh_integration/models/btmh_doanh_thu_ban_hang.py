# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BTMHDoanhThuBanHang(models.Model):
    """Model chứa dữ liệu doanh thu bán hàng từ BTMH POS"""
    _name = 'btmh.doanh_thu.ban_hang'
    _description = 'BTMH - Doanh Thu Ban Hang'
    _order = 'ngay_phieu desc, stt'
    _rec_name = 'display_name'
    
    # Thông tin phiếu bán
    id_phieu = fields.Char('ID Phiếu BTMH', required=True, index=True)
    ngay_phieu = fields.Date('Ngày Phiếu', required=True, index=True)
    stt = fields.Integer('STT Dòng', required=True)
    
    # Thông tin sản phẩm
    ten_nhom_san_pham = fields.Selection([
        ('tich_tru', 'Tích trữ'),
        ('ts_vang_24k', 'TS. vàng 24K'),
        ('ts_vang_tay', 'TS. vàng tây'),
        ('hon_hop', 'Hỗn hợp')
    ], string='Tên Nhóm Sản Phẩm')
    
    ten_dong_sp = fields.Char('Tên Dòng SP')
    nhom_hang = fields.Char('Nhóm Hàng') 
    ma_hang = fields.Char('Mã Hàng', required=True, index=True)
    ten_hang = fields.Char('Tên Hàng', required=True)
    
    # Thông tin trọng lượng và chất lượng
    ham_luong_vang = fields.Char('Hàm Lượng Vàng')
    don_vi_tinh = fields.Char('Đơn Vị Tính')
    so_luong = fields.Float('Số Lượng', digits=(16, 6))
    
    tong_trong_luong = fields.Float('Tổng Trọng Lượng', digits=(16, 6))
    trong_luong_vang_bac = fields.Float('TL Vàng/Bạc', digits=(16, 6))
    trong_luong_da = fields.Float('TL Đá', digits=(16, 6))
    
    # Thông tin giá cả
    tien_cong_ban = fields.Monetary('Tiền Công Bán', currency_field='currency_id')
    tien_cong_ban_nt = fields.Monetary('Tiền Công Bán NT', currency_field='currency_id') 
    tien_cong_mua = fields.Monetary('Tiền Công Mua', currency_field='currency_id')
    tien_cong_mua_nt = fields.Monetary('Tiền Công Mua NT', currency_field='currency_id')
    
    tien_da_ban = fields.Monetary('Tiền Đá Bán', currency_field='currency_id')
    tien_da_ban_nt = fields.Monetary('Tiền Đá Bán NT', currency_field='currency_id')
    tien_da_mua = fields.Monetary('Tiền Đá Mua', currency_field='currency_id')
    tien_da_mua_nt = fields.Monetary('Tiền Đá Mua NT', currency_field='currency_id')
    
    gia_ban_tg = fields.Monetary('Giá Bán TG', currency_field='currency_id')
    gia_ban_tg_nt = fields.Monetary('Giá Bán TG NT', currency_field='currency_id')
    gia_mua_tg = fields.Monetary('Giá Mua TG', currency_field='currency_id')
    gia_mua_tg_nt = fields.Monetary('Giá Mua TG NT', currency_field='currency_id')
    
    ty_gia_vang_mua = fields.Monetary('Tỷ Giá Vàng Mua', currency_field='currency_id')
    ty_gia_vang_mua_tg = fields.Monetary('Tỷ Giá Vàng Mua TG', currency_field='currency_id')
    
    # Thông tin bán hàng
    don_gia_ban = fields.Monetary('Đơn Giá Bán', currency_field='currency_id')
    thanh_tien_theo_dg_ban = fields.Monetary('Thành Tiền Theo ĐG Bán', currency_field='currency_id')
    
    # Thông tin giảm giá và chiết khấu
    ty_le_giam_gia_tp = fields.Float('% Giảm Giá TP', digits=(5, 2))
    tien_giam_gia_tp = fields.Monetary('Tiền Giảm Giá TP', currency_field='currency_id')
    ck_phan_bo = fields.Monetary('CK Phân Bổ', currency_field='currency_id')
    ck_the_phan_bo = fields.Monetary('CK Thẻ Phân Bổ', currency_field='currency_id')
    ck_the_cn_phan_bo = fields.Monetary('CK Thẻ CN Phân Bổ', currency_field='currency_id')
    ck_the_mg_phan_bo = fields.Monetary('CK Thẻ MG Phân Bổ', currency_field='currency_id')
    
    thanh_tien_sau_giam_gia = fields.Monetary('Thành Tiền Sau Giảm Giá', currency_field='currency_id')
    
    # Thông tin điểm bán
    nhan_vien_quay = fields.Char('Nhân Viên Quầy')
    ktq_da_xn = fields.Char('KTQ Đã XN')
    ma_quay = fields.Char('Mã Quầy')
    
    # Thông tin khách hàng
    ma_khach_hang = fields.Char('Mã Khách Hàng', index=True)
    ten_khach_hang = fields.Char('Tên Khách Hàng')
    so_dien_thoai = fields.Char('Số Điện Thoại')
    ngay_sinh = fields.Date('Ngày Sinh')
    gioi_tinh = fields.Char('Giới Tính')
    quan_huyen = fields.Char('Quận/Huyện')
    tinh_tp = fields.Char('Tỉnh/TP')
    
    # Thông tin nhà cung cấp
    ma_ncc = fields.Char('Mã NCC')
    
    # Thông tin hệ thống
    ma_thay_doi_tl = fields.Char('Mã Thay Đổi TL')
    
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
    hoa_don_odoo_id = fields.Many2one('account.move', 'Hóa Đơn Odoo', ondelete='set null')
    khach_hang_odoo_id = fields.Many2one('res.partner', 'Khách Hàng Odoo', ondelete='set null')
    san_pham_odoo_id = fields.Many2one('product.product', 'Sản Phẩm Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ', 
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('id_phieu', 'ma_hang', 'ten_hang')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.id_phieu} - {record.ma_hang} - {record.ten_hang}"
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            # Map dữ liệu từ SQL sang Odoo fields
            vals = {
                'id_phieu': btmh_data.get('ID phieu'),
                'stt': btmh_data.get('Stt', 0),
                'ten_nhom_san_pham': self._map_nhom_san_pham(btmh_data.get('Ten nhom san pham')),
                'ten_dong_sp': btmh_data.get('Ten dong SP'),
                'nhom_hang': btmh_data.get('Nhom hang'),
                'ma_hang': btmh_data.get('Ma hang'),
                'ten_hang': btmh_data.get('Ten hang'),
                'ham_luong_vang': btmh_data.get('HL vang'),
                'don_vi_tinh': btmh_data.get('Dvt'),
                'so_luong': float(btmh_data.get('So luong', 0)),
                'tong_trong_luong': float(btmh_data.get('Tong tlg', 0)),
                'trong_luong_vang_bac': float(btmh_data.get('Tlg Vang/Bac', 0)),
                'trong_luong_da': float(btmh_data.get('Tlg Da', 0)),
                'don_gia_ban': float(btmh_data.get('Don gia ban', 0)),
                'thanh_tien_theo_dg_ban': float(btmh_data.get('Thanh tien theo DG ban', 0)),
                'ty_le_giam_gia_tp': float(btmh_data.get('% giam gia TP', 0)),
                'tien_giam_gia_tp': float(btmh_data.get('Tien giam gia TP', 0)),
                'thanh_tien_sau_giam_gia': float(btmh_data.get('Thanh tien Sau giam gia', 0)),
                'nhan_vien_quay': btmh_data.get('Nhan vien quay'),
                'ktq_da_xn': btmh_data.get('KTQ DAXN'),
                'ma_quay': btmh_data.get('Ma quay'),
                'ma_khach_hang': btmh_data.get('Ma_KH', '').replace('*', ''),
                'ten_khach_hang': btmh_data.get('Ten_KH'),
                'so_dien_thoai': btmh_data.get('So_DT', '').replace('*', ''),
                'ngay_sinh': btmh_data.get('Ngay_Sinh'),
                'gioi_tinh': btmh_data.get('Gioi tinh'),
                'quan_huyen': btmh_data.get('Quan/Huyen'),
                'tinh_tp': btmh_data.get('Tinh/TP'),
                'ma_ncc': btmh_data.get('Ma NCC'),
                'ma_thay_doi_tl': btmh_data.get('Ma thay doi TL'),
                'trang_thai_sync': 'cho_sync'
            }
            
            # Parse ngày từ Sngay (format YYMMDD)
            sngay = btmh_data.get('Ngay phieu thu')
            if sngay:
                vals['ngay_phieu'] = self._parse_sngay_to_date(sngay)
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating BTMH sales data: {e}")
            raise UserError(f"Lỗi tạo dữ liệu bán hàng: {e}")
    
    def _map_nhom_san_pham(self, ten_nhom):
        """Map tên nhóm sản phẩm"""
        mapping = {
            'Tich tru': 'tich_tru',
            'TS. vang 24K': 'ts_vang_24k', 
            'TS. vang tay': 'ts_vang_tay',
            'Hon hop': 'hon_hop'
        }
        return mapping.get(ten_nhom, False)
    
    def _parse_sngay_to_date(self, sngay):
        """Convert Sngay (YYMMDD) to date"""
        try:
            if isinstance(sngay, str) and len(sngay) == 6:
                year = 2000 + int(sngay[:2])
                month = int(sngay[2:4])
                day = int(sngay[4:6])
                return fields.Date.from_string(f"{year}-{month:02d}-{day:02d}")
        except:
            pass
        return fields.Date.today()
    
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
                
                # Tạo hóa đơn
                invoice = record._create_invoice(partner, product)
                record.hoa_don_odoo_id = invoice.id
                
                record.trang_thai_sync = 'da_sync'
                record.ngay_sync = fields.Datetime.now()
                record.loi_sync = False
                
                # Ghi log
                self.env['btmh.sync.log'].create({
                    'ten_model': 'btmh.doanh_thu.ban_hang',
                    'id_ban_ghi': record.id,
                    'loai_sync': 'manual',
                    'trang_thai': 'thanh_cong',
                    'thong_bao': f'Đồng bộ thành công phiếu {record.id_phieu}'
                })
                
            except Exception as e:
                record.trang_thai_sync = 'loi'
                record.loi_sync = str(e)
                _logger.error(f"Error syncing record {record.id}: {e}")
                
                # Ghi log lỗi
                self.env['btmh.sync.log'].create({
                    'ten_model': 'btmh.doanh_thu.ban_hang',
                    'id_ban_ghi': record.id,
                    'loai_sync': 'manual',
                    'trang_thai': 'loi',
                    'thong_bao': f'Lỗi đồng bộ: {str(e)}'
                })
    
    def _get_or_create_partner(self):
        """Tạo hoặc tìm khách hàng"""
        if not self.ma_khach_hang:
            return self.env.ref('base.res_partner_1')  # Default partner
        
        partner = self.env['res.partner'].search([
            ('ref', '=', self.ma_khach_hang)
        ], limit=1)
        
        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.ten_khach_hang or self.ma_khach_hang,
                'ref': self.ma_khach_hang,
                'phone': self.so_dien_thoai,
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
            product = self.env['product.product'].create({
                'name': self.ten_hang or self.ma_hang,
                'default_code': self.ma_hang,
                'type': 'product',
                'list_price': self.don_gia_ban,
                'standard_price': self.don_gia_ban * 0.8,  # Cost price
                'sale_ok': True,
                'purchase_ok': True
            })
        
        return product
    
    def _create_invoice(self, partner, product):
        """Tạo hóa đơn bán hàng"""
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': self.ngay_phieu,
            'invoice_origin': f'BTMH-{self.id_phieu}',
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': self.ten_hang,
                'quantity': self.so_luong,
                'price_unit': self.don_gia_ban,
                'discount': self.ty_le_giam_gia_tp
            })]
        })
        
        return invoice
