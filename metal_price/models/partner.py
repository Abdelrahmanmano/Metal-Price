# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_metal_price_qty = fields.Float(compute='calc_total_metal_price_qty')

    def calc_total_metal_price_qty(self):
        self.total_metal_price_qty = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]
        domain = [
            ('have_weight_uom', '=', True),
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]
        invoice_ids = self.env['account.move'].search(domain)
        if invoice_ids:
            for partner, child_ids in all_partners_and_children.items():
                qty = 0
                for invoice in invoice_ids:
                    if invoice.partner_id.id in child_ids:
                        qty += sum(invoice.invoice_line_ids.mapped('quantity'))
                partner.total_metal_price_qty = qty

    def action_view_partner_metal_price(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("metal_price.action_move_metal_price_invoice")
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('partner_id', 'in', all_child.ids),
            ('have_weight_uom', '=', True),
        ]
        action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale',
                             'search_default_unpaid': 1, 'active_test': False}
        return action

