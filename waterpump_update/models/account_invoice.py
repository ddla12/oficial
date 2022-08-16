# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class accountmovewp(models.Model):
    _inherit = "account.move"

    x_partner_email = fields.Char(related='partner_id.email', readonly=True)

    def action_post(self):
        # _logger.info('>> action_post: entro')
        for move in self:
            if self.x_document_type == 'FE' and not self.partner_id.email:
                raise ValidationError('El cliente seleccionado no tiene asignado correo para el envío de la Factura Electrónica')
            else:
                super(accountmovewp, move).action_post()