# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate Demo',
    'depends': [
        'base_setup'
    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml'
    ],
    'installable': True,
    'application': True,
}