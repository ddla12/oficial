# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _calculate_margin(self, move, price_list, margin_price):
        msg = ''
        new_price = margin_price
        po_line = move.purchase_line_id
        if po_line.currency_id != price_list.currency_id:
            new_price = po_line.currency_id._convert(new_price, price_list.currency_id, po_line.company_id, fields.Date.context_today(self))

        item = price_list.item_ids.filtered(
                lambda r: (r.product_id == move.product_id) or (r.product_tmpl_id == move.product_tmpl_id and r.product_id == move.product_id))
        if item and item.fixed_price != new_price:
            msg += ' Producto: %s  %s --> %s \n' % (item.product_tmpl_id.name, str(item.fixed_price), str(new_price))
            item.write({"fixed_price": new_price})
        elif not item:
            # No existe por lo que registra el artículo en la lista
            msg += ' Producto: %s  %s \n' % (item.product_tmpl_id.name, str(new_price))
            self.env['product.pricelist.item'].create({'pricelist_id': price_list.id,
                                                        'product_tmpl_id': move.product_tmpl_id.id,
                                                        'product_id': move.product_id.id,
                                                        'applied_on': '0_product_variant',
                                                        'base': 'list_price',
                                                        'currency_id': price_list.currency_id.id,
                                                        'compute_price': 'fixed',
                                                        'fixed_price': new_price})
        if msg:
            msg = price_list.name + ' ' + msg
        return msg

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if res and self.picking_type_code == 'incoming':

            get_param = lambda param: self.env['ir.config_parameter'].sudo().get_param(param)
            margin_first_pricelist_id = self.env['product.pricelist'].browse(int(get_param('sale_price_by_margin.margin_first_pricelist_id')))
            margin_second_pricelist_id = self.env['product.pricelist'].browse(int(get_param('sale_price_by_margin.margin_second_pricelist_id')))

            if margin_first_pricelist_id or margin_second_pricelist_id:
                move_ids = self.move_ids_without_package
                msg = ''
                for move in move_ids.filtered(lambda m: m.purchase_line_id):
                    product = self.env['product.template'].search([('id', '=', move.product_tmpl_id.id)], limit=1)
                    if product.x_margin_first:
                        msg = msg + self._calculate_margin(move, margin_first_pricelist_id, move.purchase_line_id.x_margin_first_price)
                    if product.x_margin_second:
                        msg = msg + self._calculate_margin(move, margin_second_pricelist_id, move.purchase_line_id.x_margin_second_price)
                if msg:
                    msg = 'Se actualizó los siguientes precios de los siguientes artículos:\n '+msg
                    self.purchase_id.message_post(body=msg)
        return res
