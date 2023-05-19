# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import math


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

    @api.depends('price_unit', 'quantity', 'discount', 'tax_ids')
    def _compute_totals(self):
        if self.env.context.get('from_onchange', False):
            return
        for line in self:
            taxes = line.tax_ids.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                                             line.move_id.currency_id, line.quantity, product=line.product_id,
                                             partner=line.move_id.partner_id)
            line.update({
                'price_subtotal': taxes['total_excluded'],
                'price_total': taxes['total_included'],
            })

    @api.onchange('price_total')
    def _inverse_totals(self):
        new_context = self.env.context.copy()
        new_context['from_onchange'] = True
        self.env.context = new_context
        tax_amount = sum(tax.amount for tax in self.tax_ids)
        self.with_context(from_onchange=True).price_subtotal = self.price_total * 100 / (100 + tax_amount)
        self.with_context(from_onchange=True).price_unit = self.price_subtotal / self.quantity
        self.with_context(from_onchange=True).move_id._compute_amount()

    @api.onchange('price_subtotal')
    def _inverse_subtotals(self):
        new_context = self.env.context.copy()
        new_context['from_onchange'] = True
        self.env.context = new_context
        tax_amount = sum(tax.amount for tax in self.tax_ids)
        self.with_context(from_onchange=True).price_unit = self.price_subtotal / self.quantity
        self.with_context(from_onchange=True).move_id._compute_amount()

    @api.constrains('quantity', 'product_id')
    def check_quantity(self):
        category = self.env.ref('uom.product_uom_categ_kgm')
        for rec in self:
            if rec.quantity <= 0 and rec.uom_category_id == category:
                raise ValidationError("Quantity should be positive")

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

    def truncate(self, f, n):
        return math.ceil(f * 10 ** n) / 10 ** n
