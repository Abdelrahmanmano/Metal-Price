# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    uom_category_id = fields.Many2one('uom.category', related='product_uom_id.category_id')
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_totals',
        inverse='_inverse_subtotals',
        store=True,
        currency_field='currency_id',
    )
    price_total = fields.Monetary(
        string='Total',
        compute='_compute_totals',
        inverse='_inverse_totals',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('price_total')
    def _inverse_totals(self):
        tax_amount = sum(tax.amount for tax in self.tax_ids)
        self.price_subtotal = self.price_total * 100 / (100 + tax_amount)
        self.price_unit = self.price_subtotal / self.quantity

    @api.depends('price_subtotal')
    def _inverse_subtotals(self):
        self.price_unit = self.price_subtotal / self.quantity

    @api.onchange('price_subtotal', 'price_total', 'quantity')
    def _onchange_subtotal(self):
        if not self.quantity and self.uom_category_id == self.env.ref('uom.product_uom_categ_kgm'):
            self.price_subtotal = False
            self.price_total = False
            warning = {
                'warning': {
                    'title': _("set total when there is no quantity"),
                    'message': _("You should set quantity first"),
                }
            }
            return warning

    @api.constrains('quantity', 'product_id')
    def check_quantity(self):
        category = self.env.ref('uom.product_uom_categ_kgm')
        for rec in self:
            if rec.quantity <= 0 and rec.uom_category_id == category:
                raise ValidationError("Quantity should be positive")
