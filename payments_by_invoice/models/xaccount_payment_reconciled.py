# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api, _
from datetime import datetime


class XAccountPaymentReconciled(models.Model):
    _name = "xaccount.payment.reconciled"
    _description = "Payment view for reconciled invoices"
    _auto = False

    INVOICE_MOVE_TYPES = [
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ]
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")
    payment_id = fields.Many2one(comodel_name="account.payment", string="Payment")
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    payment_amount = fields.Monetary(string="Payment total", currency_field="currency_id")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    invoice_user_id = fields.Many2one(comodel_name="res.users", string="Salesperson")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_amount_total = fields.Monetary(string="Invoice Total", currency_field="currency_id")
    invoice_amount_residual = fields.Monetary(string="Invoice Amount Residual", currency_field="currency_id")
    invoice_move_type = fields.Selection(selection=INVOICE_MOVE_TYPES, string="Invoice Type")
    invoice_payment_term_id = fields.Many2one(related="invoice_id.invoice_payment_term_id", string="Payment Term")
    payment_date = fields.Date(related="payment_id.date", string="Payment Date")
    paid_in = fields.Float(string="Paid in")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE or REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    invoice.currency_id AS currency_id,
                    payment.id AS payment_id,
                    part.debit_amount_currency AS payment_amount,
                    invoice.id AS invoice_id,
                    invoice.company_id AS company_id,
                    invoice.invoice_user_id,
                    invoice.invoice_date,
                    CASE WHEN (amove.date - invoice.invoice_date) > 0 THEN amove.date - invoice.invoice_date ELSE 0 END AS paid_in,
                    invoice.amount_total AS invoice_amount_total,
                    invoice.amount_residual AS invoice_amount_residual,
                    invoice.move_type AS invoice_move_type
                FROM account_payment payment
                JOIN account_move amove ON amove.id = payment.move_id
                JOIN account_move_line line ON line.move_id = amove.id
                JOIN account_partial_reconcile part ON
                    part.debit_move_id = line.id
                    OR
                    part.credit_move_id = line.id
                JOIN account_move_line counterpart_line ON
                    part.debit_move_id = counterpart_line.id
                    OR
                    part.credit_move_id = counterpart_line.id
                JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                JOIN account_account account ON account.id = line.account_id
                WHERE account.internal_type IN ('receivable', 'payable')
                    AND line.id != counterpart_line.id
                    AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                GROUP BY payment.id, invoice.id, paid_in, part.debit_amount_currency
        )''' % (self._table,))
