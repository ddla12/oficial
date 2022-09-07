# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _


class resPartner(models.Model):
    _inherit = "res.partner"

    x_documents_ads_ids = fields.Many2many(comodel_name="xdocuments.comercial.ads",
                                            relation="xdocuments_ads_res_partner",
                                            string='Document ADS')
