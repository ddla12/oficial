# -*- coding: utf-8 -*-

from odoo import fields, models, api, _ 
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _get_default_picking_type_id(self):
        picking_type = None
        if self.env.context['active_id']:
            move = self.env['account.move'].browse(self.env.context['active_id'])
            order = None
            if move.move_type == 'out_invoice':
                # por ser una factura de venta, se debe crear la recepción de los productos devueltos
                order = self.env['sale.order'].search([('invoice_ids', 'in', move.ids)], limit=1)
            elif move.move_type == 'in_invoice':
                # por ser una factura de compra, se debe crear una salida de los productos a devolver al proveedor
                order = self.env['purchase.order'].search([('invoice_ids', 'in', move.ids)], limit=1)
            if order:
                for picking in order.picking_ids:
                    picking_type = picking.picking_type_id.return_picking_type_id
        return picking_type

    def _get_stock_picking_type_id(self):
        return self._get_default_picking_type_id()

    x_default_picking_type_id = fields.Integer(string='default tipo oper', default=_get_default_picking_type_id, store=False)
    x_picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                        default=_get_stock_picking_type_id,
                                        help="Indica el tipo de movimiento de inventario")

    def _prepare_default_reversal(self, move):
        data = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        data['x_picking_type_id'] = self.x_picking_type_id.id
        return data


class xStockPicking(models.Model):
    _inherit = 'stock.picking'

    x_account_move_id = fields.Integer(string='account move id')


class xStockMove(models.Model):
    _inherit = 'stock.move'

    x_account_move_line_id = fields.Integer(string='account move line id')


class xAccountMove(models.Model):
    _inherit = 'account.move'

    def _get_stock_type_id(self):
        if self._context.get('default_move_type') == '-out_invoice':
            picking_type_id = self.env['stock.picking.type'].search([('company_id', '=', self.env.company.id), ('code', '=', 'outgoing')], limit=1)
        elif self._context.get('default_move_type') == '-in_invoice':
            picking_type_id = self.env['stock.picking.type'].search([('company_id', '=', self.env.company.id), ('code', '=', 'incoming')], limit=1)
        else:
            return None
        return picking_type_id

    x_picking_code = fields.Char(compute='_compute_picking_code')
    x_picking_count = fields.Integer(string="Count", copy=False)
    x_invoice_picking_id = fields.Many2one('stock.picking', string="Picking", copy=False)

    x_picking_type_id = fields.Many2one('stock.picking.type', 'Mov.Inventario',
                                      default=_get_stock_type_id,
                                      help="Indica el tipo de movimiento de inventario")
    x_sale_order_id = fields.Many2one("sale.order", string="Cotización", copy=False,
                                      help='Cotización que originó la factura')

    def _compute_picking_code(self):
        for r in self:
            r.x_picking_code = {'out_invoice': 'outgoing', 'in_invoice': 'incoming'}.get(r.move_type)

    def action_post(self):
        res = super(xAccountMove, self).action_post()
        for move in self:
            if not move.x_from_sale and move.x_picking_type_id and not move.x_invoice_picking_id:
                # El picking de facturación solo se hace para Notas de Credito
                if move.move_type in ('out_refund', 'in_refund'):
                    move.create_stock_picking()
                elif  move.move_type in ('out_invoice','in_invoice'):
                    move.x_picking_type_id = None
        return res

    def action_create_stock_picking(self):
        if not self.is_invoice() or self.x_invoice_picking_id:
            return
        if not self.x_picking_type_id:
            raise ValidationError("Debe seleccionar el tipo de picking")
        self.create_stock_picking()

    def create_stock_picking(self):
        if len(self.invoice_line_ids.filtered(lambda r: r.product_id.type in ('consu', 'product'))) == 0:
            return
        # if self.x_picking_type_id.code == 'outgoing':
        #     data = {
        #         'location_dest_id': self.partner_id.property_stock_customer.id,
        #         'location_id': self.x_picking_type_id.default_location_src_id.id,
        #         }
        # elif self.x_picking_type_id.code == 'incoming':
        #     data = {
        #         'location_dest_id': self.x_picking_type_id.default_location_dest_id.id,
        #         'location_id': self.partner_id.property_stock_supplier.id,
        #         }
        if self.move_type == 'out_refund':
            location_id = self.partner_id.property_stock_customer.id
            location_dest_id = self.x_picking_type_id.default_location_dest_id.id
        elif self.move_type == 'in_refund':
            location_id = self.partner_id.property_stock_supplier.id
            location_dest_id = self.x_picking_type_id.default_location_dest_id.id
        else:
            raise ValidationError("Se espera que el código de tipo de operación sea de 'Entrega' o 'Recibo'")
        if not location_dest_id:
            raise ValidationError("El tipo de operación: %s, no tiene configurado la localización destino")
            data = {
                'x_account_move_id': self.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': self.x_picking_type_id.id,
                'partner_id': self.partner_id.id,
                'origin': self.name,
                'move_type': 'direct'
                }

            picking = self.env['stock.picking'].create(data)
            self.x_invoice_picking_id = picking.id
            self.x_picking_count = len(picking)

        moves = self.invoice_line_ids.filtered(lambda r: r.product_id.type in ['product', 'consu']).line_create_stock_moves(picking)
        move_ids = moves._action_confirm()
        move_ids._action_assign()

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.x_invoice_picking_id.id)]
        pick_ids = sum([self.x_invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result


class xAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def line_create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            # if picking.picking_type_id.code == 'outgoing':
            #     data = {
            #         'location_dest_id': line.move_id.partner_id.property_stock_customer.id,
            #         'location_id': picking.picking_type_id.default_location_src_id.id,
            #     }
            # if picking.picking_type_id.code == 'incoming':
            #     data = {
            #         'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
            #         'location_id': line.move_id.partner_id.property_stock_supplier.id,
            #     }
                data = {
                'x_account_move_line_id': line.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'picking_id': picking.id,
                'state': 'draft',
                'company_id': line.move_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': picking.picking_type_id.id,
                'route_ids': 1 and [
                    (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.quantity
            tmp = data.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            data['product_uom_qty'] = diff_quantity
            done += moves.create(data)
        return done
