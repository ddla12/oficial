# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    affects_stock = fields.Boolean(string="Affects Stock", default=False)

    @api.onchange('default_location_src_id')
    def _onchange_default_location_src_id(self):
        picking_ids = self.env['stock.picking'].search([('picking_type_id', '=', self._origin.id)])
        if picking_ids:
            alert = {'title': _('Action denied'),
                     'message': _(
                         'It is not possible to modify the origin if there are already movements linked to it.\nPlease contact an Administrator.')}
            return {'value': {'default_location_src_id': self._origin.default_location_src_id.id}, 'warning': alert}

    @api.onchange('default_location_dest_id')
    def _onchange_default_location_dest_id(self):
        picking_ids = self.env['stock.picking'].search([('picking_type_id', '=', self._origin.id)])
        if picking_ids:
            alert = {'title': _('Action denied'),
                     'message': _(
                         'It is not possible to modify the destination if there are already movements linked to it.\nPlease contact an Administrator.')}
            return {'value': {'default_location_dest_id': self._origin.default_location_dest_id.id}, 'warning': alert}
