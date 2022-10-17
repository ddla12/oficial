# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_cost_is_editable = fields.Boolean(default=True, compute='_compute_cost_is_editable', store=False)

    def _compute_cost_is_editable(self):
        for product in self:
            product.x_cost_is_editable = self.env.user.has_group('purchase.group_purchase_manager')