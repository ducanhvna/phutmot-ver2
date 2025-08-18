# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BTMHChungTuThanhToan(models.Model):
    """Model chứa dữ liệu chứng từ thanh toán từ BTMH POS"""
    _name = 'btmh.chung_tu.thanh_toan'
    _description = 'BTMH - Chung Tu Thanh Toan'
    _order = 'ngay_chung_tu desc, so_phieu'
    _rec_name = 'display_name'
    
    # Thông tin chứng từ
    id_chung_tu = fields.Char('ID Chứng Từ', required=True, index=True)
    so_phieu = fields.Char('Số Phiếu', required=True)
    ngay_chung_tu = fields.Date('Ngày Chứng Từ', required=True, index=True)
    stt = fields.Integer('STT Dòng')
    
    # Mã loại chứng từ
    ma_dt_no = fields.Char('Mã ĐT Nợ')
    ma_dt_co = fields.Char('Mã ĐT Có')
    
    ma_ct = fields.Selection([
        ('BC', 'Bán Chuyển khoản'),
        ('BN', 'Bán Ngoại tệ'),
        ('PT', 'Phiếu Thu'),
        ('PC', 'Phiếu Chi'),
        ('PTCK', 'PT Chuyển khoản'),
        ('PTTM', 'PT Tiền mặt'),
        ('PCCK', 'PC Chuyển khoản'),
        ('PCTM', 'PC Tiền mặt'),
        ('BCCK', 'BC Chuyển khoản'),
        ('BCTM', 'BC Tiền mặt'),
        ('BNCK', 'BN Chuyển khoản'),
        ('BNTM', 'BN Tiền mặt')
    ], string='Mã Chứng Từ', index=True)
    
    loai_ct = fields.Selection([
        ('ban_le', 'Bán lẻ'),
        ('mua_lai', 'Mua lại'),
        ('dat_coc', 'Đặt cọc'),
        ('tc_cho_phep', 'TC Cho phép')
    ], string='Loại Chứng Từ')
    
    # Thông tin tài khoản
    tk_no = fields.Char('TK Nợ', required=True)
    tk_co = fields.Char('TK Có', required=True) 
    dien_giai = fields.Text('Diễn Giải')
    so_tien = fields.Monetary('Số Tiền', currency_field='currency_id', required=True)
    
    # Thông tin ngân hàng
    ma_ngan_hang = fields.Char('Mã Ngân Hàng')
    ten_ngan_hang = fields.Char('Tên Ngân Hàng')
    so_tk_ngan_hang = fields.Char('Số TK Ngân Hàng')
    
    # Thông tin đối tượng
    ma_doi_tuong = fields.Char('Mã Đối Tượng', index=True)
    ten_khach_hang = fields.Char('Tên Khách Hàng')
    
    # Thông tin hạch toán
    h_toan = fields.Char('Hạch Toán')
    
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
    phieu_thu_chi_odoo_id = fields.Many2one('account.payment', 'Phiếu Thu/Chi Odoo', ondelete='set null')
    but_toan_odoo_id = fields.Many2one('account.move', 'Bút Toán Odoo', ondelete='set null')
    khach_hang_odoo_id = fields.Many2one('res.partner', 'Khách Hàng Odoo', ondelete='set null')
    ngan_hang_odoo_id = fields.Many2one('res.partner.bank', 'Ngân Hàng Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ', 
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('so_phieu', 'ma_ct', 'so_tien')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.so_phieu} - {record.ma_ct} - {record.so_tien:,.0f}"
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'id_chung_tu': str(btmh_data.get('ID')),
                'ma_dt_no': btmh_data.get('MaDT_No'),
                'ma_dt_co': btmh_data.get('MaDT_Co'),
                'ma_ct': btmh_data.get('Ma_Ct'),
                'so_phieu': btmh_data.get('Sp'),
                'h_toan': btmh_data.get('H.Toan'),
                'stt': btmh_data.get('Stt', 0),
                'loai_ct': self._map_loai_ct(btmh_data.get('Loai_CT')),
                'tk_no': btmh_data.get('No_Tk', '').replace('*', ''),
                'tk_co': btmh_data.get('Co_Tk', '').replace('*', ''),
                'dien_giai': btmh_data.get('Dien_giai'),
                'so_tien': float(btmh_data.get('So_tien', 0)),
                'ma_ngan_hang': btmh_data.get('Ma_NganHang'),
                'ten_ngan_hang': btmh_data.get('Ten_NH'),
                'so_tk_ngan_hang': btmh_data.get('So_TK'),
                'ma_doi_tuong': btmh_data.get('Ma_DoiTuong', '').replace('*', ''),
                'ten_khach_hang': btmh_data.get('Ten_KhachHang'),
                'trang_thai_sync': 'cho_sync'
            }
            
            # Parse ngày từ Sngay
            sngay = btmh_data.get('Sngay')
            if sngay:
                vals['ngay_chung_tu'] = self._parse_sngay_to_date(sngay)
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating BTMH payment data: {e}")
            raise UserError(f"Lỗi tạo dữ liệu chứng từ: {e}")
    
    def _map_loai_ct(self, loai_ct):
        """Map loại chứng từ"""
        mapping = {
            'Ban le': 'ban_le',
            'Mua lai': 'mua_lai',
            'Dat coc': 'dat_coc',
            'TC_ChoPhep': 'tc_cho_phep'
        }
        return mapping.get(loai_ct, False)
    
    def _parse_sngay_to_date(self, sngay):
        """Convert Sngay (YYMMDD) to date"""
        try:
            if isinstance(sngay, int):
                sngay = str(sngay)
            if len(sngay) == 6:
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
                
                # Tạo phiếu thu/chi hoặc bút toán tùy thuộc loại
                if record.ma_ct in ['PT', 'PC', 'PTCK', 'PTTM', 'PCCK', 'PCTM']:
                    payment = record._create_payment()
                    record.phieu_thu_chi_odoo_id = payment.id
                else:
                    journal_entry = record._create_journal_entry()
                    record.but_toan_odoo_id = journal_entry.id
                
                record.trang_thai_sync = 'da_sync'
                record.ngay_sync = fields.Datetime.now()
                record.loi_sync = False
                
                # Ghi log
                self.env['btmh.sync.log'].create({
                    'ten_model': 'btmh.chung_tu.thanh_toan',
                    'id_ban_ghi': record.id,
                    'loai_sync': 'manual',
                    'trang_thai': 'thanh_cong',
                    'thong_bao': f'Đồng bộ thành công chứng từ {record.so_phieu}'
                })
                
            except Exception as e:
                record.trang_thai_sync = 'loi'
                record.loi_sync = str(e)
                _logger.error(f"Error syncing record {record.id}: {e}")
    
    def _create_payment(self):
        """Tạo phiếu thu/chi"""
        payment_type = 'inbound' if self.ma_ct.startswith('PT') else 'outbound'
        payment_method = 'manual'
        
        # Tìm journal phù hợp
        if 'CK' in self.ma_ct:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        
        # Tìm hoặc tạo partner
        partner = self._get_or_create_partner()
        
        payment = self.env['account.payment'].create({
            'payment_type': payment_type,
            'partner_type': 'customer' if payment_type == 'inbound' else 'supplier',
            'partner_id': partner.id if partner else False,
            'amount': abs(self.so_tien),
            'date': self.ngay_chung_tu,
            'ref': self.so_phieu,
            'journal_id': journal.id,
            'payment_method_line_id': journal.inbound_payment_method_line_ids[0].id if payment_type == 'inbound' else journal.outbound_payment_method_line_ids[0].id
        })
        
        return payment
    
    def _create_journal_entry(self):
        """Tạo bút toán"""
        journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        
        # Tìm tài khoản từ chart of accounts
        account_no = self.env['account.account'].search([
            ('code', '=', self.tk_no[:6])  # Lấy 6 ký tự đầu
        ], limit=1)
        
        account_co = self.env['account.account'].search([
            ('code', '=', self.tk_co[:6])  # Lấy 6 ký tự đầu  
        ], limit=1)
        
        if not account_no:
            account_no = self.env['account.account'].search([('code', 'like', self.tk_no[:4])], limit=1)
        if not account_co:
            account_co = self.env['account.account'].search([('code', 'like', self.tk_co[:4])], limit=1)
        
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': self.ngay_chung_tu,
            'ref': self.so_phieu,
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': self.dien_giai or 'BTMH Transfer',
                    'account_id': account_no.id if account_no else journal.default_account_id.id,
                    'debit': self.so_tien,
                    'credit': 0
                }),
                (0, 0, {
                    'name': self.dien_giai or 'BTMH Transfer',
                    'account_id': account_co.id if account_co else journal.default_account_id.id,
                    'debit': 0,
                    'credit': self.so_tien
                })
            ]
        })
        
        return move
    
    def _get_or_create_partner(self):
        """Tạo hoặc tìm đối tượng"""
        if not self.ma_doi_tuong:
            return False
        
        partner = self.env['res.partner'].search([
            ('ref', '=', self.ma_doi_tuong)
        ], limit=1)
        
        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.ten_khach_hang or self.ma_doi_tuong,
                'ref': self.ma_doi_tuong,
                'is_company': False,
                'customer_rank': 1,
                'supplier_rank': 1
            })
        
        return partner
