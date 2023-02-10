# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class posorderwp(models.Model):
    _inherit = "pos.order"

    x_name_to_print = fields.Char(string='Nombre Factura', copy=True, readonly=False)

    def action_print_ticket_pos_order(self):
        if self._is_pos_order_paid():
            return self.env.ref('pos_extensionfe.pos_order_invoice_report').report_action(self)

    def action_get_payment(self):
        if self.x_document_type == 'FE' and not self.partner_id.email:
            raise ValidationError('El cliente seleccionado no tiene asignado correo para el envío de la Factura Electrónica')
        return super(posorderwp, self).action_get_payment()

    @api.onchange('session_id')
    def change_session(self):
        for data in self:
            msg = ('Se asigno la session: %s' % (data.session_id.name))
            self.message_post(body=msg)
