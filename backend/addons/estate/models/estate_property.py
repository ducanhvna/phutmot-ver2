from odoo import models, fields
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Test Odoo Model"

    name = fields.Char(required=False, string="Chao ban", help="Đây là một tool tip cho bạn dễ thao tác", index = False)
    description = fields.Text(string='Description')
    date_availability = fields.Date(string='Available From', default = lambda self: fields.Date.today() + relativedelta(months=3))
    date_availability = fields.Date(string='Available From', dedault = lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly = True)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string='Garden Orientation'
    )
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
    [
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ],
    required=True, copy=False, default='new'
)

