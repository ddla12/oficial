# -*- coding: utf-8 -*-
# from odoo import http


# class WaterpumpUpdate(http.Controller):
#     @http.route('/waterpump_update/waterpump_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/waterpump_update/waterpump_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('waterpump_update.listing', {
#             'root': '/waterpump_update/waterpump_update',
#             'objects': http.request.env['waterpump_update.waterpump_update'].search([]),
#         })

#     @http.route('/waterpump_update/waterpump_update/objects/<model("waterpump_update.waterpump_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('waterpump_update.object', {
#             'object': obj
#         })
