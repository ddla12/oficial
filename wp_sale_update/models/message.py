# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PettyCashConfirm(models.TransientModel):
    _name = 'message.alert'

    type_message = fields.Selection([
        ('message', 'Mensaje'),
        ('alert', 'Alerta'),
        ('confirm', 'Confirmación'),
        ('error', 'Error'),
    ], default='alert', required=True)
    model_type = fields.Char()
    function = fields.Char()
    message = fields.Text(required=True, readonly=True)
    model_data_id = fields.Integer()

    def set_alert(self, message, type_message, model_type, function, id):
        action = self.env.ref('wp_sale_update.action_message_alert')
        result = action.read()[0]
        if message != 'message':
            message_id = self.create(
                {'message': message, 'type_message': type_message, 'model_type': model_type, 'function': function, 'model_data_id': id})
        else:
            message_id = self.create({'message': message, 'type_message': type_message})
        res = self.env.ref('alert.message_confirm_form_view', False)
        form_view = [(res and res.id or False, 'form')]
        result['views'] = form_view
        result['res_id'] = message_id.id
        return result

    def confirm(self):
        if self.function:
            data = self.env[self.model_type].search([('id', '=', self.model_data_id)])
            getattr(data, self.function)()
