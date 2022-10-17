# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(string='Order Types',
                                  selection=[('prduction_order', 'Type of Order Production'),
                                             ('stock_order', 'Type of Order Stock')], default="prduction_order",)
    x_name_to_print = fields.Char(string='Nombre Factura', copy=True)

    def _prepare_pos_order_data(self, opened_session):
        res = super(SaleOrder, self)._prepare_pos_order_data(opened_session)
        if self.x_name_to_print:
            res['x_name_to_print'] = self.x_name_to_print
        return res

    @api.onchange("partner_id")
    def _onchange_partner_id_name_to_print(self):
        if self.partner_id:
            self.x_name_to_print = self.partner_id.name