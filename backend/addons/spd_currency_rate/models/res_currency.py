# -*- coding: utf-8 -*-

from odoo import models,api
import requests

class InheritResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_currency_rate(self):
        access_token = self.env['ir.config_parameter'].sudo().get_param('spd_currency_rate.access_token')
        if not access_token:
            return

        url = f'https://v6.exchangerate-api.com/v6/{access_token}/latest/USD'

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return

        data = response.json()

        if data.get('result') != 'success':
            return

        rates = data.get('conversion_rates')
        if not rates:
            return

        currencies = self.search([])
        updated_currencies = []

        for currency in currencies:
            if not currency.is_current_company_currency:
                rate = rates.get(currency.name)
                if rate:
                    latest_rate_line = currency.rate_ids
                    latest_rate_line.write({'company_rate' : rate})
                    updated_currencies.append(currency.name)
