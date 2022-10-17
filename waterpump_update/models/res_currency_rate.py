# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class xResCurrencyRateUpdate(models.Model):
    _inherit = 'res.currency.rate'

    @api.constrains('rate')
    def _check_rate(self):
        for rec in self:
            if (((rec.company_id and rec.company_id.currency_id != rec.currency_id and rec.currency_id.name == 'USD')
                 or (not rec.company_id and rec.currency_id.name == 'USD')) and rec.rate > 0.01):
                raise ValidationError("W: El tipo de cambio para dólares para el día %s es incorrecto. "
                                      " Valor: %s" % (rec.name.strftime("%d-%b-%Y").replace('.', ''), str(rec.rate)))
