# -*- coding: utf-8 -*-

from odoo import _,api, fields, models

class CurrencyRateSample(models.TransientModel):
    _inherit = 'res.config.settings'
    
    access_token = fields.Char(string='Access Token',
                               config_parameter='spd_currency_rate.access_token')