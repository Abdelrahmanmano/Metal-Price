# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    uom_category_id = fields.Many2one('uom.category', related='product_uom_id.category_id')
    price_subtotal = fields.Monetary(
        inverse='_inverse_subtotals'
    )
    price_total = fields.Monetary(
        inverse='_inverse_totals'
    )

    @api.depends('price_total')
    def _inverse_totals(self):
        tax_val = self.price_total - self.price_total * (1 - (15 / 100.0))
        self.price_subtotal = self.price_total - tax_val
        self.price_unit = (self.price_total - tax_val) / self.quantity

    @api.depends('price_subtotal')
    def _inverse_subtotals(self):
        self.price_unit = self.price_subtotal / self.quantity

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']
                line.price_total = taxes_res['total_included']
            else:
                line.price_total = line.price_subtotal = subtotal

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
