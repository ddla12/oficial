from odoo import fields, models, api, _

class AccountCashboxLineExtend(models.Model):
    _inherit = 'account.cashbox.line'
    _order = 'x_currency_id asc, coin_value'

    @api.depends('coin_value', 'number', 'x_rate')
    def _sub_total(self):
        """ Calculates Sub total"""
        for cashbox_line in self:
            cashbox_line.subtotal = (cashbox_line.coin_value*cashbox_line.number) / cashbox_line.x_rate

    x_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id,
                                    string='Tipo de Moneda',domain="[('active', '=', True)]")
    x_rate = fields.Float(string='Tasa de Cambio',related='x_currency_id.rate')

    x_cr_rate_selling = fields.Float(string='Factor de Cambio', compute='_compute_cr_rate_selling')

    @api.depends('x_currency_id')
    def _compute_cr_rate_selling(self):
        for line in self:
            if line.x_currency_id.name == 'USD':
                line.x_cr_rate_selling = round(1/line.x_rate,2)
            else:
                line.x_cr_rate_selling = 1
