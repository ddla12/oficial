# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
# from ast import Store

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_margin_first_price = fields.Float(string='Precio Márgen 1', compute="_compute_product_price", store=True)
    x_margin_second_price = fields.Float(string='Precio Márgen 2', compute="_compute_product_price", store=True)
    x_old_standard_price = fields.Float(string='Precio pasado', readonly=True, store=True)
    x_margin_first = fields.Float(string='% Margen Precio 1', compute="_compute_margin")
    x_margin_second = fields.Float(string='% Margen Precio 2', compute="_compute_margin")


    @staticmethod
    def _calculate_margin_price(margin, price_unit, round_factor):
        margin_price = round((price_unit * (1 + margin / 100)) / round_factor, 0) * round_factor
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

    @api.depends('price_unit')
    def _compute_margin(self):
        for line in self:
            line.x_margin_first = round(((line.x_margin_first_price - line.price_unit) / line.price_unit) * 100, 1) if line.x_margin_first_price > 0 else None
            line.x_margin_second = round(((line.x_margin_second_price - line.price_unit) / line.price_unit) * 100, 1) if line.x_margin_second_price > 0 else None
