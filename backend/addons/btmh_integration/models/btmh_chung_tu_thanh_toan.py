# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BTMHChungTuThanhToan(models.Model):
    """Model chứa dữ liệu chứng từ thanh toán từ BTMH POS - Dong tien POS"""
    _name = 'btmh.chung_tu.thanh_toan'
    _description = 'BTMH - Chung Tu Thanh Toan (Dong Tien POS)'
    _order = 'sngay desc, ma_ct, sp'
    _rec_name = 'display_name'
    
    # Thông tin chứng từ chính - từ SlTcD
    id_chung_tu = fields.Char('ID Chứng Từ BTMH', required=True, index=True, help="SlTcD.ID")
    
    # Mã địa điểm theo tài khoản
    ma_dt_no = fields.Selection([
        ('TMDT', 'TMDT'),
        ('VPT', 'VPT'),
        ('CH1', 'CH1'), ('CH2', 'CH2'), ('CH3', 'CH3'), ('CH4', 'CH4'), 
        ('CH5', 'CH5'), ('CH6', 'CH6'), ('CH7', 'CH7'), ('CH8', 'CH8'), ('CH9', 'CH9'),
    ], string='Mã ĐT Nợ', help="Địa điểm từ No_Tk")
    
    ma_dt_co = fields.Selection([
        ('TMDT', 'TMDT'),
        ('VPT', 'VPT'), 
        ('CH1', 'CH1'), ('CH2', 'CH2'), ('CH3', 'CH3'), ('CH4', 'CH4'),
        ('CH5', 'CH5'), ('CH6', 'CH6'), ('CH7', 'CH7'), ('CH8', 'CH8'), ('CH9', 'CH9'),
    ], string='Mã ĐT Có', help="Địa điểm từ Co_Tk")
    
    # Thông tin ngày
    sngay = fields.Integer('Số Ngày BTMH', required=True, index=True, help="Format: YYMMDD")
    ngay_chung_tu = fields.Date('Ngày Chứng Từ', compute='_compute_ngay_chung_tu', store=True)
    
    # Mã chứng từ theo logic BTMH
    ma_ct = fields.Selection([
        ('BC', 'Bán Chuyển khoản'),  # 1121->xxx
        ('BN', 'Bán Ngoại tệ'),     # 1121<-xxx  
        ('PT', 'Phiếu Thu'),        # 1111->xxx
        ('PC', 'Phiếu Chi'),        # 1111<-xxx
        ('PTCK', 'PT Chuyển khoản'), # 1111->1121
        ('PTTM', 'PT Tiền mặt'),    # 1111->1111
        ('PCCK', 'PC Chuyển khoản'), # 1121->1111  
        ('PCTM', 'PC Tiền mặt'),    # 1111->1111
        ('BCCK', 'BC Chuyển khoản'), # 1121->1121
        ('BCTM', 'BC Tiền mặt'),    # 1121->1111
        ('BNCK', 'BN Chuyển khoản'), # 1121<-1121
        ('BNTM', 'BN Tiền mặt')     # 1111<-1121
    ], string='Mã Chứng Từ', index=True)
    
    # Thông tin phiếu
    sp = fields.Char('Số Phiếu', help="SlTcM.Sp")
    h_toan = fields.Char('Hạch Toán', help="DmNx.Ma_Nx")
    stt = fields.Integer('STT Dòng', help="SlTcD.Stt")
    
    # Loại chứng từ
    loai_ct = fields.Selection([
        ('ban_le', 'Bán lẻ'),       # SlTcM.LoaiCt='F'
        ('mua_lai', 'Mua lại'),     # SlTcM.LoaiCt='G'  
        ('dat_coc', 'Đặt cọc'),     # SlTcM.LoaiCt='H'
        ('tc_cho_phep', 'TC Cho phép') # Ma_Nx in ('TTH','TCK','CTM','CKMH')
    ], string='Loại Chứng Từ')
    
    # Thông tin tài khoản - với dấu *
    no_tk = fields.Char('TK Nợ', required=True, help="Với dấu * đầu")
    co_tk = fields.Char('TK Có', required=True, help="Với dấu * đầu")
    
    # Diễn giải và số tiền
    dien_giai = fields.Text('Diễn Giải', help="fTCVNToUnicode(SlTcD.Dien_Giai)")
    so_tien = fields.Monetary('Số Tiền', currency_field='currency_id', help="FORMAT(SlTcD.T_Tien,'0')")
    
    # Thông tin ngân hàng
    ma_ngan_hang = fields.Char('Mã Ngân Hàng', help="DmNHang.Ma_Nh")
    ten_ngan_hang = fields.Char('Tên Ngân Hàng', help="fTCVNToUnicode(DmNHang.Ten_Nh)")
    so_tk_ngan_hang = fields.Char('Số TK Ngân Hàng', help="DmNHang.So_Tk")
    
    # Thông tin đối tượng (khách hàng)
    ma_doi_tuong = fields.Char('Mã Đối Tượng', help="Với dấu * đầu - DmDt.Ma_Dt")
    ten_khach_hang = fields.Char('Tên Khách Hàng', help="fTCVNToUnicode(Ten_Dt)")
    
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
    journal_entry_id = fields.Many2one('account.move', 'Bút Toán Odoo', ondelete='set null')
    partner_id = fields.Many2one('res.partner', 'Đối Tác Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ', 
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('sngay', 'ma_ct', 'sp', 'so_tien')
    def _compute_display_name(self):
        for record in self:
            ngay_str = str(record.sngay) if record.sngay else ''
            record.display_name = f"{record.ma_ct} - {record.sp} - {ngay_str} - {record.so_tien:,.0f}"
    
    @api.depends('sngay')
    def _compute_ngay_chung_tu(self):
        """Chuyển đổi Sngay (YYMMDD) sang Date"""
        for record in self:
            if record.sngay:
                try:
                    sngay_str = str(record.sngay).zfill(6)  # Đảm bảo 6 ký tự
                    year = int(sngay_str[:2]) + 2000
                    month = int(sngay_str[2:4])
                    day = int(sngay_str[4:6])
                    record.ngay_chung_tu = fields.Date(year, month, day)
                except:
                    record.ngay_chung_tu = False
            else:
                record.ngay_chung_tu = False
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'id_chung_tu': btmh_data.get('ID'),
                'ma_dt_no': btmh_data.get('MaDT_No'),
                'ma_dt_co': btmh_data.get('MaDT_Co'), 
                'sngay': btmh_data.get('Sngay'),
                'ma_ct': btmh_data.get('Ma_Ct'),
                'sp': btmh_data.get('Sp'),
                'h_toan': btmh_data.get('H.Toan'),
                'stt': btmh_data.get('Stt'),
                'loai_ct': self._map_loai_ct(btmh_data.get('Loai_CT')),
                'no_tk': btmh_data.get('No_Tk'),  # Đã có dấu *
                'co_tk': btmh_data.get('Co_Tk'),  # Đã có dấu *
                'dien_giai': btmh_data.get('Dien_giai'),
                'so_tien': self._parse_currency(btmh_data.get('So_tien')),
                'ma_ngan_hang': btmh_data.get('Ma_NganHang'),
                'ten_ngan_hang': btmh_data.get('Ten_NH'),
                'so_tk_ngan_hang': btmh_data.get('So_TK'),
                'ma_doi_tuong': btmh_data.get('Ma_DoiTuong'),  # Đã có dấu *
                'ten_khach_hang': btmh_data.get('Ten_KhachHang'),
                'trang_thai_sync': 'chua_sync'
            }
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Lỗi tạo chứng từ thanh toán từ BTMH data: {str(e)}")
            raise UserError(f"Không thể tạo chứng từ: {str(e)}")
    
    def _map_loai_ct(self, loai_ct_str):
        """Map loại chứng từ từ BTMH sang Odoo"""
        mapping = {
            'Ban le': 'ban_le',
            'Mua lai': 'mua_lai', 
            'Dat coc': 'dat_coc',
            'TC_ChoPhep': 'tc_cho_phep'
        }
        return mapping.get(loai_ct_str, False)
    
    def _parse_currency(self, currency_str):
        """Parse currency string sang float"""
        if not currency_str:
            return 0.0
        try:
            # Loại bỏ dấu phẩy và parse
            return float(str(currency_str).replace(',', ''))
        except:
            return 0.0
    
    @api.model
    def sync_from_btmh_database(self, ngay_hom_nay=None):
        """Sync dữ liệu từ BTMH database"""
        # Implementation để connect và pull data từ SQL Server
        # Sẽ implement sau khi có connection string
        pass
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
    
    @api.depends('sp', 'ma_ct', 'so_tien')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.sp} - {record.ma_ct} - {record.so_tien:,.0f}"
    
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
