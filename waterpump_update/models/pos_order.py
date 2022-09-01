# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class posorderwp(models.Model):
    _inherit = "pos.order"

    def action_get_payment(self):
        if self.x_document_type == 'FE' and not self.partner_id.email:
            raise ValidationError('El cliente seleccionado no tiene asignado correo para el envío de la Factura Electrónica')
        return super(posorderwp, self).action_get_payment()