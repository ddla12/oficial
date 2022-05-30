from odoo import fields, models, api, _

class AccountCashboxLineExtend(models.Model):
    _inherit = 'account.cashbox.line'

    @api.depends('coin_value', 'number', 'x_rate')
    def _sub_total(self):
        """ Calculates Sub total"""
        for cashbox_line in self:
            cashbox_line.subtotal = (cashbox_line.coin_value*cashbox_line.number) / cashbox_line.x_rate

    x_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id,
                                    string='Tipo de Moneda',domain="[('active', '=', True)]")
    x_rate = fields.Float(string='Tasa de Cambio',related='x_currency_id.rate')

