# -*- coding: utf-8 -*-

from odoo import models, api, fields
import requests
import string
import random

class InheritResCurrency(models.Model):
    _inherit = 'res.currency'

    def _generate_currency_code(self, loai_vang):
        # Generate code from first 3 letters of loai_vang
        code = ''.join(c for c in loai_vang[:3].upper() if c.isalpha())
        
        if not code:
            # If no valid letters found, generate random code
            code = 'GH' + ''.join(random.choices(string.digits, k=1))
            
        # Check if code exists
        while self.search_count([('name', '=', code)]) > 0:
            code = 'GH' + ''.join(random.choices(string.digits, k=1))
            
        return code

    @api.model
    def _get_currency_rate(self):
        access_token = self.env['ir.config_parameter'].sudo().get_param('spd_currency_rate.access_token')
        if not access_token:
            return

        url = 'https://tigia.baotinmanhhai.vn/api/getTyGia'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-type': 'Application/json; charset=utf-8'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return

        data = response.json()

        if data.get('status') != 200:
            return

        gold_rates = data.get('data', [])
        if not gold_rates:
            return

        # Get VND currency for reference
        vnd_currency = self.env.ref('base.VND')
        
        for rate_data in gold_rates:
            loai_vang = rate_data.get('loaiVang')
            if not loai_vang:
                continue

            # Find or create currency
            currency_code = rate_data.get('maLoaivang') or self._generate_currency_code(loai_vang)
            currency = self.search([('name', '=', currency_code)], limit=1)
            
            if not currency:
                # Create new currency
                currency = self.create({
                    'name': currency_code,
                    'symbol': loai_vang,
                    'rate_ids': [(0, 0, {
                        'name': fields.Date.today(),
                        'company_rate': 1.0
                    })]
                })

            # Update rate
            buy_price = rate_data.get('giaMuaNiemYet', 0)
            if buy_price:
                rate = vnd_currency.rate / buy_price if buy_price else 0
                if rate:
                    currency.rate_ids.write({'company_rate': rate})
