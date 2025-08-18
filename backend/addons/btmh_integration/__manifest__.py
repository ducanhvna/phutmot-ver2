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
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
