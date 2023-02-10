# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

class accountmovewp(models.Model):
    _inherit = "account.move"

    x_delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_sale_picking_ids')
    x_last_picking_date_done = fields.Date('Última entrega válida', compute='_compute_last_picking_date_done')
    x_due_days_count = fields.Integer(string='Días atraso pago', compute='_compute_due_days_count')
    x_name_to_print = fields.Char(string='Nombre Factura', copy=True, readonly=False)

    @api.depends('invoice_date_due')
    def _compute_due_days_count(self):
        for move in self:
            move.x_due_days_count = 0
            if move.invoice_date_due and move.move_type in ['out_invoice']:
                date_today = date.today()
                days_count = date_today - move.invoice_date_due

                if days_count and days_count.days > 0:
                    payments = self.env['account.payment.register'].search([('line_ids.id', 'in', move.line_ids.ids)],
                                                                           order='payment_date desc')
                    if payments and payments[0].payment_date and move.amount_residual == 0:
                        payment_days_count = payments[0].payment_date - move.invoice_date_due
                        if payment_days_count and payment_days_count.days > 0:
                            move.x_due_days_count = payment_days_count.days+1
                    else:
                        move.x_due_days_count = days_count.days+1

    def _compute_last_picking_date_done(self):
        for move in self:
            move.x_last_picking_date_done = None
            if move.move_type == 'out_invoice':
                sale_order = move._get_sale_order()
                if sale_order and sale_order.picking_ids:
                    picking_list = sale_order.picking_ids.filtered(
                        lambda x: x.state == 'done' and x.location_dest_id.usage == 'customer')
                    if picking_list:
                        move.x_last_picking_date_done = max([picking_id.date_done for picking_id in picking_list]). \
                                                            date() or None

    def _get_sale_order(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].search([('invoice_ids', 'in', (self.ids))], limit=1)
        return sale_order

    def _compute_sale_picking_ids(self):
        for move in self:
            if move.move_type == 'out_invoice':
                sale_order = move._get_sale_order()
                if sale_order:
                    move.x_delivery_count = len(sale_order.picking_ids) or 0
                else:
                    move.x_delivery_count = 0
            else:
                move.x_delivery_count = 0

    def action_view_sale_delivery(self):
        sale_order = self._get_sale_order()
        return sale_order.action_view_delivery()

    def action_post(self):
        for move in self:
            if move.x_document_type == 'FE' and not move.partner_id.email:
                raise ValidationError('El cliente seleccionado no tiene asignado correo para el envío de la Factura Electrónica')
            else:
                super(accountmovewp, move).action_post()