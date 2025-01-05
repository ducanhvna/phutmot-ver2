# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vyshnav AR(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class LocationDetail(models.Model):
    """This model represents comprehensive details about locations within
     the context of agriculture. It provides a structured way to store
     information related to various geographic locations, such as farms, fields,
      or storage areas. """
    _name = 'location.detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Location Details In Agriculture Details"
    _rec_name = 'location_name'

    location_name = fields.Char(string='Location Name', required=True,
                                help='Give the name of Location where'
                                     ' farming done', tracking=True)
    code = fields.Char(string='Location Code', required=False,
                                help='Give the Code of location', tracking=True)
    
    location_address = fields.Char(string='Location Address', required=True,
                                   help='Give the full address of the location',
                                   tracking=True)
    location_area = fields.Float(string='Location Area', required=True,
                                 help='The area of location', tracking=True)
    location_area_unit = fields.Selection([('acres', 'Acres'),
                                           ('hectares', 'Hectares')],
                                          string='Area Unit', tracking=True,
                                          required=True,
                                          help='Mention the units of area')
    location_type = fields.Selection([('plot', 'Plot'),
                                      ('field', 'Field')], default="plot",
                                     required=True, tracking=True,
                                     help='Describe the type of farming area',
                                     string='Location Type')
    district_id = fields.Many2one('res.country.district', string='Huyện', domain="[('state_id', '=', state_id)]")
    ward_id = fields.Many2one('res.country.ward', string='Xã', domain="[('district_id', '=', district_id)]")
    state_id = fields.Many2one("res.country.state", string='Tỉnh', ondelete='restrict',
                               domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', default=241, string='Quốc gia', ondelete='restrict')
    note = fields.Text(string='Note', tracking=True,
                       help='If any description for the location, mention here')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        readonly=True, help='The company associated with the current user or '
        'environment.', default=lambda self: self.env.company)
