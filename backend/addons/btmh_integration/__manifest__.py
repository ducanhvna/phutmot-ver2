# -*- coding: utf-8 -*-
{
    'name': 'BTMH Integration',
    'version': '18.0.1.0.0',
    'category': 'Integration',
    'summary': 'Integration between BTMH POS System and Odoo ERP via Microsoft Fabric',
    'description': '''
        This module provides integration between BTMH POS system and Odoo ERP.
        Features:
        - Sync sales data from BTMH to Odoo invoices
        - Sync payment transactions
        - Sync deposit/pre-orders
        - Real-time data sync via Microsoft Fabric
        - Comprehensive logging and error handling
    ''',
    'author': 'BTMH Development Team',
    'depends': ['base', 'account', 'sale', 'stock', 'base_accounting_kit'],
    'data': [
        'security/ir.model.access.csv',
        
        # Views cho các models mới với tên tiếng Việt
        'views/btmh_doanh_thu_ban_hang_views.xml',
        'views/btmh_chung_tu_thanh_toan_views.xml',
        'views/btmh_dat_coc_views.xml',
        'views/btmh_du_dau_ngay_views.xml',
        'views/btmh_nhat_ky_dong_bo_views.xml',
        
        # Views cũ (commented for backward compatibility)
        # 'views/btmh_sales_data_views.xml',
        # 'views/btmh_payment_data_views.xml',
        # 'views/btmh_deposit_data_views.xml',
        # 'views/btmh_sync_log_views.xml',
        
        'views/btmh_fabric_pipeline_views.xml',
        'views/btmh_menu.xml',
        'data/cron_jobs.xml',
        
        # Data files cũ (commented)
        # 'data/btmh_cron_jobs.xml',
        # 'data/btmh_sequence_data.xml',
    ],
    'demo': [
        'demo/fabric_pipelines_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
