# -*- coding: utf-8 -*-
{
    'name': 'Real-Time Currency Rate Update',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Automatically update currency exchange rates from external API in real-time or scheduled',
    'description': '''
        This module enables automatic and real-time updating of currency exchange rates
        using a configurable external API service. It includes:
        - Configurable API URL in settings
        - Automatic updates via scheduled cron job
        - Manual update option from settings
        - Currency Rate Update
        - Currency Rate Update using API
    ''',
    'author': 'SPD Solutions',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'data/currency_rate_cron.xml',
        'views/res_config_settings.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
