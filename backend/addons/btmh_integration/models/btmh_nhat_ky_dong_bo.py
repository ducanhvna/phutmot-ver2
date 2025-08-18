# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class BTMHNhatKyDongBo(models.Model):
    """Model ghi log quá trình đồng bộ dữ liệu BTMH"""
    _name = 'btmh.nhat_ky_dong_bo'
    _description = 'BTMH - Nhat Ky Dong Bo'
    _order = 'ngay_tao desc'
    _rec_name = 'display_name'
    
    # Thông tin model và record
    ten_model = fields.Char('Tên Model', required=True, index=True)
    id_ban_ghi = fields.Integer('ID Bản Ghi', index=True)
    
    # Thông tin sync
    loai_sync = fields.Selection([
        ('thu_cong', 'Thủ Công'),
        ('tu_dong', 'Tự Động'),  
        ('fabric_webhook', 'Fabric Webhook'),
        ('thu_lai', 'Thử Lại'),
        ('hang_loat', 'Hàng Loạt')
    ], string='Loại Sync', required=True, default='thu_cong', index=True)
    
    trang_thai = fields.Selection([
        ('dang_xu_ly', 'Đang Xử Lý'),
        ('thanh_cong', 'Thành Công'),
        ('loi', 'Lỗi'),
        ('canh_bao', 'Cảnh Báo'),
        ('huy', 'Hủy')
    ], string='Trạng Thái', required=True, default='dang_xu_ly', index=True)
    
    thong_bao = fields.Text('Thông Báo', required=True)
    chi_tiet_loi = fields.Text('Chi Tiết Lỗi')
    
    # Thông tin thời gian
    ngay_tao = fields.Datetime('Ngày Tạo', default=fields.Datetime.now, required=True)
    thoi_gian_xu_ly = fields.Float('Thời Gian Xử Lý (giây)', digits=(8, 2))
    
    # Thông tin số lượng
    so_ban_ghi_xu_ly = fields.Integer('Số Bản Ghi Xử Lý', default=1)
    so_ban_ghi_thanh_cong = fields.Integer('Số Bản Ghi Thành Công', default=0)
    so_ban_ghi_loi = fields.Integer('Số Bản Ghi Lỗi', default=0)
    
    # System fields
    nguoi_tao_id = fields.Many2one('res.users', 'Người Tạo', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Công Ty', default=lambda self: self.env.company)
    active = fields.Boolean('Hoạt Động', default=True)
    
    display_name = fields.Char('Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    @api.depends('ten_model', 'trang_thai', 'thong_bao')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.ten_model} - {record.trang_thai} - {record.thong_bao[:50]}..."
    
    @api.model
    def tao_log(self, ten_model, id_ban_ghi=False, loai_sync='thu_cong', 
                trang_thai='thanh_cong', thong_bao='', chi_tiet_loi='', 
                thoi_gian_xu_ly=0, so_ban_ghi_xu_ly=1, 
                so_ban_ghi_thanh_cong=0, so_ban_ghi_loi=0):
        """Phương thức tạo log nhanh"""
        return self.create({
            'ten_model': ten_model,
            'id_ban_ghi': id_ban_ghi,
            'loai_sync': loai_sync,
            'trang_thai': trang_thai,
            'thong_bao': thong_bao,
            'chi_tiet_loi': chi_tiet_loi,
            'thoi_gian_xu_ly': thoi_gian_xu_ly,
            'so_ban_ghi_xu_ly': so_ban_ghi_xu_ly,
            'so_ban_ghi_thanh_cong': so_ban_ghi_thanh_cong,
            'so_ban_ghi_loi': so_ban_ghi_loi
        })
    
    @api.model
    def xoa_log_cu(self, so_ngay_giu_lai=30):
        """Xóa log cũ để tránh database quá lớn"""
        cutoff_date = fields.Datetime.now() - timedelta(days=so_ngay_giu_lai)
        old_logs = self.search([('ngay_tao', '<', cutoff_date)])
        old_logs.unlink()
        return len(old_logs)
    
    def action_xem_ban_ghi_lien_quan(self):
        """Xem bản ghi liên quan được sync"""
        if not self.ten_model or not self.id_ban_ghi:
            raise UserError("Không có thông tin bản ghi liên quan")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Bản Ghi {self.ten_model}',
            'res_model': self.ten_model,
            'res_id': self.id_ban_ghi,
            'view_mode': 'form',
            'target': 'current'
        }
