# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MetalPrice(models.Model):
    _name = 'metal.price'
    _description = 'Metal Price'
    _rec_name = 'metal_price'
    _order = 'date desc'
    _inherit = 'mail.thread'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self._default_currency_id(),
    )
    metal_price = fields.Monetary(currency_field='currency_id', string='Metal Price')
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    historical_metal_price_ids = fields.Many2many('metal.price', compute='calc_historical_metal_price_ids')

    _sql_constraints = [
        ('check_metal_price', 'CHECK(metal_price > 0)', 'The Metal price can\'t be negative or zero'),
    ]

    def _default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('metal_price', 'date')
    def calc_historical_metal_price_ids(self):
        historical_ids = self.search([])
        for rec in self:
            rec.historical_metal_price_ids = historical_ids.ids

    @api.model_create_multi
    def create(self, vals):
        result = super(MetalPrice, self).create(vals)
        return result
