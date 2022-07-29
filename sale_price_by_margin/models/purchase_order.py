# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
# from ast import Store


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_margin_first_price = fields.Float(string='Precio Márgen 1', compute="_compute_product_price", store=True)
    x_margin_second_price = fields.Float(string='Precio Márgen 2', compute="_compute_product_price", store=True)
    x_old_standard_price = fields.Float(string='Precio pasado', readonly=True, store=True)

    @staticmethod
    def _calculate_margin_price(margin, price_unit, round_factor):
        margin_price = price_unit * (1 + margin / 100)
        if round_factor > 0:
            cociente, residuo = divmod(margin_price, round_factor)
            if residuo > 0:
                margin_price = (cociente * round_factor) + round_factor
        return margin_price

    @api.onchange('x_old_standard_price')
    def _onchange_old_price_unit(self):
        self.ensure_one
        if self.product_id:
            self.x_old_standard_price = self.product_id.product_tmpl_id.standard_price

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        self.ensure_one()
        self.x_old_standard_price = self.product_id.product_tmpl_id.standard_price

    @api.depends('price_unit')
    def _compute_product_price(self):
        for line in self:
            line.x_margin_first_price = 0
            line.x_margin_second_price = 0
            if line.product_id and line.price_unit:
                product_tmpl = line.product_id.product_tmpl_id
                if product_tmpl.x_margin_first:
                    line.x_margin_first_price = line._calculate_margin_price(product_tmpl.x_margin_first, line.price_unit, product_tmpl.x_round_factor)
                if product_tmpl.x_margin_second:
                    line.x_margin_second_price = line._calculate_margin_price(product_tmpl.x_margin_second, line.price_unit, product_tmpl.x_round_factor)
