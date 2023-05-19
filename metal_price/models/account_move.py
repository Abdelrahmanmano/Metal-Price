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

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        if self.env.context.get('from_onchange', False):
            return
        super(AccountMove, self)._compute_amount()
        for move in self:
            move.amount_untaxed = sum(move.line_ids.mapped('price_subtotal'))
            move.amount_tax = sum(move.line_ids.mapped('price_total')) - sum(move.line_ids.mapped('price_subtotal'))
            move.amount_total = sum(move.line_ids.mapped('price_total'))
            move.amount_residual = sum(move.line_ids.mapped('price_total'))

