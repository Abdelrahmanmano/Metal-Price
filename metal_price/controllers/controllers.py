# -*- coding: utf-8 -*-
# from odoo import http


# class MetalPrice(http.Controller):
#     @http.route('/metal_price/metal_price', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metal_price/metal_price/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('metal_price.listing', {
#             'root': '/metal_price/metal_price',
#             'objects': http.request.env['metal_price.metal_price'].search([]),
#         })

#     @http.route('/metal_price/metal_price/objects/<model("metal_price.metal_price"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metal_price.object', {
#             'object': obj
#         })
