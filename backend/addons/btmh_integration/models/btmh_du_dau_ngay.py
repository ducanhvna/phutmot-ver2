# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import date, datetime

_logger = logging.getLogger(__name__)

class BTMHDuDauNgay(models.Model):
    """Model chứa dữ liệu dư đầu ngày tiền mặt/chuyển khoản từ BTMH POS"""
    _name = 'btmh.du_dau_ngay'
    _description = 'BTMH - Du Dau Ngay Dong Tien'
    _order = 'ngay_cap_nhat desc, ma_tk'
    _rec_name = 'display_name'
    
    # Thông tin tài khoản - với dấu *
    ma_tk = fields.Char('Mã Tài Khoản', required=True, index=True, help="Với dấu * đầu")
    
    # Mã chi nhánh
    ma_ch = fields.Selection([
        ('CH1', 'Cửa Hàng 1'),   # 111101, 112101
        ('CH2', 'Cửa Hàng 2'),   # 111102, 112102  
        ('CH3', 'Cửa Hàng 3'),   # 111103, 112103
        ('CH4', 'Cửa Hàng 4'),   # 111104, 112104
        ('CH5', 'Cửa Hàng 5'),   # 111105, 112105
        ('CH6', 'Cửa Hàng 6'),   # 111106, 112106
        ('CH7', 'Cửa Hàng 7'),   # 111107, 112107
        ('CH8', 'Cửa Hàng 8'),   # 111108, 112108
        ('CH9', 'Cửa Hàng 9'),   # 111109, 112109, 1111G9, 1121G9
        ('TMDT', 'Thương Mại Điện Tử'), # 111100, 112100
        ('VPT', 'Văn Phòng Trung Tâm')  # 1111VP, 1111VPT, 1121VP, 1121VTB, 1121.ACB2-, 1121GN
    ], string='Mã Chi Nhánh', required=True, index=True)
    
    # Loại tài khoản  
    loai = fields.Selection([
        ('TM', 'Tiền Mặt'),      # 1111xx
        ('TK', 'Tài Khoản')      # 1121xx
    ], string='Loại TK', required=True, index=True)
    
    # Số dư
    no_dky = fields.Monetary('Nợ Đầu Kỳ', currency_field='currency_id', 
                             help="SUM(ISNULL(No_DauKy/No_Dky, 0))")
    co_dky = fields.Monetary('Có Đầu Kỳ', currency_field='currency_id',
                             help="SUM(ISNULL(Co_DauKy/Co_Dky, 0))")  
    du_dky = fields.Monetary('Dư Đầu Kỳ', currency_field='currency_id',
                             help="No_Dky - Co_Dky", compute='_compute_du_dky', store=True)
    
    # Thông tin thời gian
    ngay_cap_nhat = fields.Date('Ngày Cập Nhật', required=True, index=True, default=fields.Date.today)
    la_ngay_dau_thang = fields.Boolean('Là Ngày Đầu Tháng', compute='_compute_la_ngay_dau_thang', store=True)
    
    # Metadata từ SQL
    nam = fields.Integer('Năm', help="Sdtk.Nam từ SQL")
    thang = fields.Integer('Tháng', help="Sdtk.Mm từ SQL") 
    
    # Trạng thái
    trang_thai_sync = fields.Selection([
        ('chua_sync', 'Chưa Sync'),
        ('dang_sync', 'Đang Sync'),
        ('da_sync', 'Đã Sync'),
        ('loi', 'Lỗi')
    ], string='Trạng Thái Sync', default='chua_sync', index=True)
    
    ngay_sync = fields.Datetime('Ngày Sync')
    loi_sync = fields.Text('Lỗi Sync')
    
    # Liên kết Odoo
    account_id = fields.Many2one('account.account', 'Tài Khoản Odoo', ondelete='set null')
    journal_id = fields.Many2one('account.journal', 'Sổ Nhật Ký Odoo', ondelete='set null')
    
    # System fields
    currency_id = fields.Many2one('res.currency', 'Tiền Tệ',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công Ty', 
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    # Constraints
    _sql_constraints = [
        ('unique_tk_ngay', 'unique(ma_tk, ngay_cap_nhat)', 
         'Mỗi tài khoản chỉ có 1 record dư đầu ngày!')
    ]
    
    @api.depends('no_dky', 'co_dky')
    def _compute_du_dky(self):
        """Tính dư đầu kỳ = Nợ - Có"""
        for record in self:
            record.du_dky = (record.no_dky or 0) - (record.co_dky or 0)
    
    @api.depends('ngay_cap_nhat')
    def _compute_la_ngay_dau_thang(self):
        """Kiểm tra có phải ngày đầu tháng không"""
        for record in self:
            if record.ngay_cap_nhat:
                record.la_ngay_dau_thang = record.ngay_cap_nhat.day == 1
            else:
                record.la_ngay_dau_thang = False
    
    @api.depends('ma_tk', 'ma_ch', 'loai', 'du_dky', 'ngay_cap_nhat')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.ma_tk} - {record.ma_ch} ({record.loai}) - {record.du_dky:,.0f} - {record.ngay_cap_nhat}"
    
    @api.model
    def create_from_btmh_data(self, btmh_data):
        """Tạo record từ dữ liệu BTMH SQL"""
        try:
            vals = {
                'ma_tk': btmh_data.get('Ma_tk'),          # Đã có dấu *
                'ma_ch': btmh_data.get('Ma_CH'),
                'loai': btmh_data.get('Loai'),  
                'no_dky': float(btmh_data.get('No_Dky', 0)),
                'co_dky': float(btmh_data.get('Co_Dky', 0)),
                # du_dky sẽ được compute tự động
                'ngay_cap_nhat': fields.Date.today(),
                'nam': datetime.now().year,
                'thang': datetime.now().month,
                'trang_thai_sync': 'chua_sync'
            }
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Lỗi tạo dư đầu ngày từ BTMH data: {str(e)}")
            raise UserError(f"Không thể tạo dư đầu ngày: {str(e)}")
    
    @api.model
    def sync_from_btmh_database(self, target_date=None):
        """
        Sync dữ liệu từ BTMH database
        Logic phức tạp:
        - Nếu là ngày đầu tháng: Lấy từ Sdtk (số dư đầu kỳ)  
        - Nếu không: Tính từ Sdtk + các giao dịch SlNxD, SlBlD, SlDcD, SlTcD
        """
        if not target_date:
            target_date = fields.Date.today()
            
        # Determine if it's first day of month
        is_first_day = target_date.day == 1
        
        if is_first_day:
            return self._sync_first_day_of_month(target_date)
        else:
            return self._sync_regular_day(target_date)
    
    def _sync_first_day_of_month(self, target_date):
        """Sync ngày đầu tháng - chỉ lấy từ Sdtk"""
        # Implementation cho query đầu tiên trong SQL
        _logger.info(f"Syncing first day of month: {target_date}")
        
        # Ma_tk_List CTE logic
        ma_tk_mapping = self._get_ma_tk_mapping()
        
        # Query Sdtk với WHERE Sdtk.Nam = @Nam AND Sdtk.ID_Dv = 0 AND Sdtk.Mm = @thang
        # GROUP BY Ma_tk_List.Ma_tk, Ma_tk_List.Ma_CH, Ma_tk_List.Loai
        
        pass
    
    def _sync_regular_day(self, target_date):
        """Sync ngày thường - tính từ đầu tháng + giao dịch"""
        # Implementation cho query thứ hai trong SQL (phức tạp hơn)
        _logger.info(f"Syncing regular day: {target_date}")
        
        # Logic UNION ALL với:
        # - Sdtk (số dư đầu kỳ)
        # - SlNxD (nhập xuất dòng)
        # - SlBlD (bán lẻ dòng)  
        # - SlDcD (đặt cọc dòng)
        # - SlTcD (thu chi dòng)
        
        pass
    
    def _get_ma_tk_mapping(self):
        """Tạo ma trận mapping Ma_tk -> Ma_CH, Loai như trong CTE"""
        return [
            ('111101', 'CH1', 'TM'), ('111102', 'CH2', 'TM'), ('111103', 'CH3', 'TM'),
            ('111104', 'CH4', 'TM'), ('111105', 'CH5', 'TM'), ('111106', 'CH6', 'TM'),
            ('111107', 'CH7', 'TM'), ('111108', 'CH8', 'TM'), ('111109', 'CH9', 'TM'),
            ('1111G9', 'CH9', 'TM'), ('111100', 'TMDT', 'TM'),
            ('1111VP', 'VPT', 'TM'), ('1111VPT', 'VPT', 'TM'),
            
            ('112101', 'CH1', 'TK'), ('112102', 'CH2', 'TK'), ('112103', 'CH3', 'TK'),
            ('112104', 'CH4', 'TK'), ('112105', 'CH5', 'TK'), ('112106', 'CH6', 'TK'),
            ('112107', 'CH7', 'TK'), ('112108', 'CH8', 'TK'), ('112109', 'CH9', 'TK'),
            ('1121G9', 'CH9', 'TK'), ('112100', 'TMDT', 'TK'),
            ('1121VP', 'VPT', 'TK'), ('1121VTB', 'VPT', 'TK'), 
            ('1121.ACB2-', 'VPT', 'TK'), ('1121GN', 'VPT', 'TK')
        ]
    
    @api.model
    def action_sync_du_dau_ngay_hom_nay(self):
        """Action button để sync dư đầu ngày hôm nay"""
        return self.sync_from_btmh_database(fields.Date.today())
    
    def action_create_odoo_journal_entry(self):
        """Tạo bút toán mở sổ trong Odoo từ dư đầu ngày"""
        for record in self:
            if abs(record.du_dky) < 0.01:  # Bỏ qua số dư = 0
                continue
                
            # Tìm hoặc tạo tài khoản kế toán
            account = record._get_or_create_account()
            record.account_id = account.id
            
            # Tìm journal phù hợp
            journal = record._get_appropriate_journal()
            record.journal_id = journal.id
            
            # Tài khoản đối ứng (equity - vốn chủ sở hữu)  
            equity_account = record._get_equity_account()
            
            # Tạo journal entry
            move_vals = {
                'move_type': 'entry',
                'date': record.ngay_cap_nhat,
                'ref': f'BTMH-DDN-{record.ma_tk}-{record.ma_ch}',
                'journal_id': journal.id,
                'line_ids': [
                    (0, 0, {
                        'name': f'Dư đầu ngày {record.ma_tk} - {record.ma_ch}',
                        'account_id': account.id,
                        'debit': record.du_dky if record.du_dky > 0 else 0,
                        'credit': abs(record.du_dky) if record.du_dky < 0 else 0
                    }),
                    (0, 0, {
                        'name': f'Dư đầu ngày {record.ma_tk} - {record.ma_ch}',
                        'account_id': equity_account.id,
                        'debit': abs(record.du_dky) if record.du_dky < 0 else 0,
                        'credit': record.du_dky if record.du_dky > 0 else 0
                    })
                ]
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            # Update sync status
            record.trang_thai_sync = 'da_sync'
            record.ngay_sync = fields.Datetime.now()
            
            _logger.info(f"Tạo bút toán dư đầu ngày {record.ma_tk}: {move.name}")
    
    def _get_or_create_account(self):
        """Tìm hoặc tạo tài khoản kế toán"""
        # Remove * prefix if present
        clean_ma_tk = self.ma_tk.lstrip('*')
        
        # Tìm theo mã tài khoản
        account = self.env['account.account'].search([
            ('code', '=', clean_ma_tk)
        ], limit=1)
        
        if not account:
            # Tạo tài khoản mới
            account_type = self._determine_account_type()
            
            account = self.env['account.account'].create({
                'name': f'BTMH {self.ma_tk} - {self.ma_ch} ({self.loai})',
                'code': clean_ma_tk,
                'account_type': account_type,
                'reconcile': True if self.loai == 'TK' else False,
            })
            
            _logger.info(f"Tạo tài khoản mới: {account.code} - {account.name}")
        
        return account
    
    def _determine_account_type(self):
        """Xác định loại tài khoản dựa vào mã"""
        clean_ma_tk = self.ma_tk.lstrip('*')
        
        if clean_ma_tk.startswith('111'):
            return 'asset_current'  # Tiền mặt
        elif clean_ma_tk.startswith('112'):
            return 'asset_current'  # Tiền gửi ngân hàng
        elif clean_ma_tk.startswith('131'):
            return 'asset_receivable'  # Phải thu khách hàng
        elif clean_ma_tk.startswith('331'):
            return 'liability_payable'  # Phải trả khách hàng
        else:
            return 'asset_current'  # Default
    
    def _get_appropriate_journal(self):
        """Tìm journal phù hợp"""
        if self.loai == 'TM':
            journal = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        
        if not journal:
            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        
        return journal
    
    def _get_equity_account(self):
        """Tìm tài khoản vốn"""
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
        
        return equity_account
    
    @api.model
    def import_daily_balance_from_sql(self, sql_query_result):
        """Import dữ liệu từ kết quả SQL query Du_dau_Ngay_Ver1.sql"""
        created_records = []
        
        for row in sql_query_result:
            try:
                # Parse data từ SQL result
                vals = {
                    'ma_tk': f"*{row['Ma_tk']}" if not str(row['Ma_tk']).startswith('*') else row['Ma_tk'],
                    'ma_ch': row['Ma_CH'],
                    'loai': row['Loai'],
                    'no_dky': float(row.get('No_Dky', 0)),
                    'co_dky': float(row.get('Co_Dky', 0)),
                    'ngay_cap_nhat': fields.Date.today(),
                    'nam': datetime.now().year,
                    'thang': datetime.now().month,
                    'trang_thai_sync': 'chua_sync'
                }
                
                # Check if record exists
                existing = self.search([
                    ('ma_tk', '=', vals['ma_tk']),
                    ('ngay_cap_nhat', '=', vals['ngay_cap_nhat'])
                ])
                
                if existing:
                    existing.write({
                        'no_dky': vals['no_dky'],
                        'co_dky': vals['co_dky'],
                        'trang_thai_sync': 'chua_sync'
                    })
                    created_records.append(existing)
                else:
                    record = self.create(vals)
                    created_records.append(record)
                    
            except Exception as e:
                _logger.error(f"Lỗi import dữ liệu dư đầu ngày: {str(e)}")
                continue
        
        _logger.info(f"Import thành công {len(created_records)} records dư đầu ngày")
        return created_records
