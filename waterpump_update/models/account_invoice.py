# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class accountmovewp(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            if move.x_document_type == 'FE' and not move.partner_id.email:
                raise ValidationError('El cliente seleccionado no tiene asignado correo para el envío de la Factura Electrónica')
            else:
                super(accountmovewp, move).action_post()