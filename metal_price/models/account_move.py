# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    metal_price_id = fields.Many2one(comodel_name='metal.price', string='Metal Price',
                                     default=lambda self: self.default_metal_price())
    have_weight_uom = fields.Boolean(compute='calc_have_weight_uom', store=True)

    def default_metal_price(self):
        metal_price = self.env['metal.price'].search([('date', '=', fields.Date.today())], limit=1, order='date desc')
        if metal_price:
            return metal_price.id
        return False

    @api.depends('metal_price_id', 'invoice_line_ids')
    def calc_have_weight_uom(self):
        for rec in self:
            rec.have_weight_uom = any(
                line.uom_category_id == self.env.ref('uom.product_uom_categ_kgm') for line in rec.invoice_line_ids)
