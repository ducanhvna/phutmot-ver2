# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BTMHDuDauNgay(models.Model):
    """Model chứa dữ liệu dư đầu ngày từ BTMH POS"""
    _name = 'btmh.du_dau_ngay'
    _description = 'BTMH - Du Dau Ngay'
    _order = 'ngay_bao_cao desc, ma_tk'
    _rec_name = 'display_name'
    
    # Thông tin báo cáo
    ngay_bao_cao = fields.Date('Ngày Báo Cáo', required=True, index=True)
    ma_tk = fields.Char('Mã Tài Khoản', required=True, index=True)
    ma_ch = fields.Char('Mã Cửa Hàng', required=True, index=True)
    loai = fields.Selection([
        ('TM', 'Tiền Mặt'),
        ('TK', 'Tài Khoản')
    ], string='Loại', required=True)
    
    # Số dư tài khoản  
    du_dau_ky = fields.Monetary('Dư Đầu Kỳ', currency_field='currency_id')
    phat_sinh_no = fields.Monetary('Phát Sinh Nợ', currency_field='currency_id')
    phat_sinh_co = fields.Monetary('Phát Sinh Có', currency_field='currency_id')
    du_cuoi_ky = fields.Monetary('Dư Cuối Kỳ', currency_field='currency_id', compute='_compute_du_cuoi_ky', store=True)
    
    # Thông tin chi tiết
    ten_tai_khoan = fields.Char('Tên Tài Khoản')
    ghi_chu = fields.Text('Ghi Chú')
    
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
    tai_khoan_odoo_id = fields.Many2one('account.account', 'Tài Khoản Odoo', ondelete='set null')
    but_toan_odoo_id = fields.Many2one('account.move', 'Bút Toán Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ', 
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty',
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('ngay_bao_cao', 'ma_tk', 'ma_ch', 'du_cuoi_ky')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.ngay_bao_cao} - {record.ma_tk} - {record.ma_ch} - {record.du_cuoi_ky:,.0f}"
    
    @api.depends('du_dau_ky', 'phat_sinh_no', 'phat_sinh_co')
    def _compute_du_cuoi_ky(self):
        for record in self:
            record.du_cuoi_ky = record.du_dau_ky + record.phat_sinh_no - record.phat_sinh_co
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'ma_tk': btmh_data.get('Ma_tk'),
                'ma_ch': btmh_data.get('Ma_CH'),
                'loai': btmh_data.get('Loai'),
                'du_dau_ky': float(btmh_data.get('DuDau', 0)),
                'phat_sinh_no': float(btmh_data.get('PhatSinhNo', 0)),
                'phat_sinh_co': float(btmh_data.get('PhatSinhCo', 0)),
                'ten_tai_khoan': btmh_data.get('TenTaiKhoan'),
                'ghi_chu': btmh_data.get('GhiChu'),
                'trang_thai_sync': 'cho_sync'
            }
            
            # Parse ngày báo cáo
            ngay_bao_cao = btmh_data.get('NgayBaoCao')
            if ngay_bao_cao:
                vals['ngay_bao_cao'] = fields.Date.from_string(ngay_bao_cao)
            else:
                vals['ngay_bao_cao'] = fields.Date.today()
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating BTMH balance data: {e}")
            raise UserError(f"Lỗi tạo dữ liệu dư đầu ngày: {e}")
    
    def action_sync_to_odoo(self):
        """Đồng bộ lên Odoo ERP"""
        for record in self:
            try:
                record.trang_thai_sync = 'cho_sync'
                
                # Tìm hoặc tạo tài khoản kế toán
                account = record._get_or_create_account()
                record.tai_khoan_odoo_id = account.id
                
                # Tạo bút toán điều chỉnh số dư (nếu cần)
                if abs(record.du_cuoi_ky) > 0:
                    journal_entry = record._create_balance_adjustment(account)
                    record.but_toan_odoo_id = journal_entry.id
                
                record.trang_thai_sync = 'da_sync'
                record.ngay_sync = fields.Datetime.now()
                record.loi_sync = False
                
                # Ghi log
                self.env['btmh.sync.log'].create({
                    'ten_model': 'btmh.du_dau_ngay',
                    'id_ban_ghi': record.id,
                    'loai_sync': 'manual',
                    'trang_thai': 'thanh_cong',
                    'thong_bao': f'Đồng bộ thành công TK {record.ma_tk} - {record.ma_ch}'
                })
                
            except Exception as e:
                record.trang_thai_sync = 'loi'
                record.loi_sync = str(e)
                _logger.error(f"Error syncing record {record.id}: {e}")
    
    def _get_or_create_account(self):
        """Tìm hoặc tạo tài khoản kế toán"""
        # Tìm theo mã tài khoản BTMH
        account = self.env['account.account'].search([
            ('code', '=', self.ma_tk)
        ], limit=1)
        
        if not account:
            # Tìm theo pattern gần giống
            account = self.env['account.account'].search([
                ('code', 'like', self.ma_tk[:4])
            ], limit=1)
        
        if not account:
            # Tạo tài khoản mới
            account_type = self._determine_account_type()
            
            account = self.env['account.account'].create({
                'name': self.ten_tai_khoan or f'BTMH {self.ma_tk}',
                'code': self.ma_tk,
                'account_type': account_type,
                'reconcile': True if self.loai == 'TK' else False,
            })
        
        return account
    
    def _determine_account_type(self):
        """Xác định loại tài khoản dựa vào mã"""
        if self.ma_tk.startswith('111'):
            return 'asset_current'  # Tiền mặt
        elif self.ma_tk.startswith('112'):
            return 'asset_current'  # Tiền gửi ngân hàng
        elif self.ma_tk.startswith('131'):
            return 'asset_receivable'  # Phải thu khách hàng
        elif self.ma_tk.startswith('331'):
            return 'liability_payable'  # Phải trả khách hàng
        else:
            return 'asset_current'  # Default
    
    def _create_balance_adjustment(self, account):
        """Tạo bút toán điều chỉnh số dư"""
        # Tìm journal phù hợp
        if self.loai == 'TM':
            journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        
        if not journal:
            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        
        # Tài khoản đối ứng (equity - vốn chủ sở hữu)
        equity_account = self.env['account.account'].search([
            ('account_type', '=', 'equity')
        ], limit=1)
        
        if not equity_account:
            # Tạo tài khoản vốn nếu chưa có
            equity_account = self.env['account.account'].create({
                'name': 'Lợi nhuận chưa phân phối',
                'code': '421',
                'account_type': 'equity'
            })
        
        # Tạo journal entry
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': self.ngay_bao_cao,
            'ref': f'BTMH-BAL-{self.ma_tk}-{self.ma_ch}',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': f'Điều chỉnh số dư {self.ma_tk} - {self.ma_ch}',
                    'account_id': account.id,
                    'debit': self.du_cuoi_ky if self.du_cuoi_ky > 0 else 0,
                    'credit': abs(self.du_cuoi_ky) if self.du_cuoi_ky < 0 else 0
                }),
                (0, 0, {
                    'name': f'Điều chỉnh số dư {self.ma_tk} - {self.ma_ch}',
                    'account_id': equity_account.id,
                    'debit': abs(self.du_cuoi_ky) if self.du_cuoi_ky < 0 else 0,
                    'credit': self.du_cuoi_ky if self.du_cuoi_ky > 0 else 0
                })
            ]
        })
        
        # Post journal entry
        move.action_post()
        
        return move
    
    @api.model
    def import_daily_balance_report(self, report_date=None):
        """Import báo cáo dư đầu ngày từ BTMH"""
        if not report_date:
            report_date = fields.Date.today()
        
        # Xóa dữ liệu cũ của ngày
        existing_records = self.search([('ngay_bao_cao', '=', report_date)])
        existing_records.unlink()
        
        # TODO: Implement API call to BTMH or Fabric to get balance data
        _logger.info(f"Importing daily balance report for {report_date}")
        
        return True
