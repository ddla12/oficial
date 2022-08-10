# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_round

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    x_discount_calc_type = fields.Char(string='Aplicar % descuento', size=2,
                                            help='valores: p=Descuento por Porcentaje, m=Descuento por Monto')
    x_amount_discount = fields.Monetary(string='Monto descuento')



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_discount_calc_type = fields.Char(string='Aplicar % descuento', size=2,
                                       help='valores: p=Descuento por Porcentaje, m=Descuento por Monto')
    x_discount = fields.Float(string="% descuento",
                              help='The discount in percentage, between 1 and 100')
    x_amount_discount = fields.Monetary(string='Monto descuento')


    @staticmethod
    def calc_amount_discount(price_subtotal, discount, precision_rounding):
        return float_round(price_subtotal * (discount / 100), precision_rounding=precision_rounding)

    @api.onchange('x_discount')
    def _onchange_x_discount(self):
        self.ensure_one()
        if self.x_discount_calc_type == 'm':
            return
        if not (0 <= self.x_discount <= 100):
            raise ValidationError("El rango de porcentaje debe estar entre 0 y 100")
        if not self.x_discount or self.x_discount == 0:
            self.x_discount_calc_type = None
            self.x_amount_discount = None
        else:
            self.x_discount_calc_type = 'p'
            self.x_amount_discount = self.calc_amount_discount((self.product_qty * self.price_unit), self.x_discount, self.order_id.currency_id.rounding)

    @api.onchange('x_amount_discount')
    def _onchange_x_amount_discount(self):
        self.ensure_one()
        if self.x_discount_calc_type == 'p' or self.x_amount_discount == 0:
            return
        self.x_discount_calc_type == 'm'
        if not (self.product_qty > 0 and self.price_unit > 0):
            self.x_amount_discount = 0

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        price_subtotal = self.product_qty * self.price_unit
        if self.x_discount_calc_type == 'p':
            discount_percent = self.x_discount
            amount_discount = self.calc_amount_discount(price_subtotal, self.x_discount, self.order_id.currency_id.rounding)
        elif price_subtotal != 0:
            discount_percent = (self.x_amount_discount / price_subtotal) * 100
            amount_discount = self.x_amount_discount
        else:
            discount_percent = None
            amount_discount = 0
        res.update({
            'x_discount_calc_type': self.x_discount_calc_type,
            'discount': discount_percent,
            'x_amount_discount': amount_discount,
            })
        return res

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'x_amount_discount')
    def _compute_amount(self):
        res = super(PurchaseOrderLine, self)._compute_amount()

        for line in self:
            price_subtotal = line.price_unit * line.product_qty
            if line.x_discount:
                x_amount_discount = float_round(price_subtotal * (line.x_discount / 100), precision_rounding=line.order_id.currency_id.rounding)
                line.update({'x_amount_discount': x_amount_discount})
            elif line.x_amount_discount > price_subtotal:
                raise UserError("El monto de descuento debe ser inferior al subtotal")
            else:
                x_amount_discount = line.x_amount_discount

            price_subtotal = price_subtotal - x_amount_discount
            total_price_tax = 0
            for tax in line.taxes_id:
                if tax.amount:
                    total_price_tax += (price_subtotal * tax.amount)/100

            line.update({
                'price_tax': total_price_tax,
                'price_subtotal': price_subtotal,
            })
