from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class FaeAccountInvoice(models.Model):
    _inherit = "account.move"

    x_overdue_bill_count_message = fields.Char('Tiene Facturas Vencidas', compute='_compute_x_overdue_bill_count_message',
                                               store=False)

    @api.depends('partner_id')
    def _compute_x_overdue_bill_count_message(self):
        self.ensure_one()
        self.x_overdue_bill_count_message = None
        if self.move_type == 'out_invoice':
            # Obtiene los montos no pagados de las facturas vencidas
            out_invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                            ('state', '=', 'posted'),
                                                            ('partner_id', '=', self.partner_id.id),
                                                            ('invoice_date_due', '<', fields.Datetime.today())])
            currency_ids = out_invoices.currency_id
            amount_residual_by_currency = []
            for currency in currency_ids:
                currency_id = self.env['res.currency'].search([('id', '=', currency.id)], limit=1)
                total_amount_residual = sum(
                    out_invoices.filtered(lambda invoice: invoice.currency_id.id == currency.id)
                        .mapped('amount_residual'))

                amount_residual_by_currency.append({
                    'currency': currency_id.name,
                    'amount_residual': total_amount_residual,
                })

            if amount_residual_by_currency:
                cant = 0
                for amount in amount_residual_by_currency:
                    if round(amount.get('amount_residual', 2)) > 0:
                        cant += 1
                        if cant == 1:
                            overdue_bill_count_message = 'Este cliente tiene facturas vencidas con pagos pendientes. \n'

                        if cant > 1:
                            overdue_bill_count_message += ', '
                        overdue_bill_count_message += str(amount.get('currency')) + ': ' + str(round(amount.get('amount_residual', 2))) + '\n'
                if cant >= 1:
                    self.x_overdue_bill_count_message = overdue_bill_count_message
