# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class xDocumentsComercialADS(models.Model):
    _name = "xdocuments.comercial.ads"
    _order = "sequence, destination_type"

    name = fields.Char('Nombre', required=True)
    sequence = fields.Integer('Secuencia', default=1, help="Usado para determinar que nota se imprime primero. Números bajos son primero")
    sequence_display = fields.Integer('Orden', compute='_compute_sequence_display')
    date_from = fields.Date(string='Fecha Inicio', required=True)
    date_to = fields.Date(string='Fecha Fin')
    data = fields.Html(string="Datos", copy=False, help='HTML con los datos de la Nota', )
    destination_type = fields.Selection(string="Tipo Destino", selection=[
                                                                ('sale', 'Cotización'),
                                                                ('invoice', 'Factura'),
                                                                ('sale-invoice', 'Cotización y Factura')],
                                        default='invoice', required=True)
    partner_type = fields.Selection(string="Tipo Contacto",
                                    selection=[('foreign', 'Foráneo'),
                                               ('local', 'Local'),
                                               ('all', 'Todos')], default='all', required=True,
                                    help='Indica que tipo de contacto (cliente/proveedor) aplica la nota')
    automatic_apply = fields.Boolean(string="Aplicar automáticamente", default=True)
    is_foreign = fields.Boolean(compute='_compute_is_foreign', store=True)
    automatic_ads_replaced_id = fields.Many2one('xdocuments.comercial.ads', string='Reemplaza Nota',
                                     domain="[('destination_type','=',destination_type), ('automatic_apply','=',True)]",
                                     help='Corresponde con el ads automático que será reemplazado')
    active = fields.Boolean(string="Activo", default=True)

    def _compute_sequence_display(self):
        for rec in self:
            rec.sequence_display = rec.sequence

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        f_hasta_max = date(2999, 12, 31)
        for ads in self:
            if not ads.date_to:
                ads.date_to = f_hasta_max
            if ads.date_from > ads.date_to:
                raise ValidationError('La fecha de inicio debe ser inferior a la fecha de fin')

    @api.constrains('destination_type', 'automatic_apply', 'automatic_ads_replaced_id')
    def check_automatic_ads_id(self):
        for ads in self:
            if ads.automatic_ads_replaced_id and (not ads.automatic_ads_replaced_id.automatic_apply
                                             or ads.destination_type != ads.automatic_ads_replaced_id.destination_type):
                ads.automatic_ads_replaced_id = False

    @api.depends('partner_type')
    def _compute_is_foreign(self):
        for ads in self:
            ads.is_foreign = (ads.partner_type == 'foreign')

    def get_document_ads(self, destination_type, document_date, partner_id):
        ads_list = []
        destination_type2 = 'sale-invoice' if destination_type in ('sale', 'invoice') else destination_type
        if not document_date:
            document_date = date.today()
        elif destination_type == 'sale':
            document_date = document_date.date()    # convierte el datetime de la cotización en date

        # ads asociados al contacto
        ads_partner = partner_id.x_documents_ads_ids.filtered(lambda a: not a.automatic_apply and a.active and a.destination_type in (destination_type, destination_type2)
                                                                and a.date_from <= document_date and document_date <= a.date_to).sorted(key=lambda r: r.sequence)

        # ads aplican automaticamente al documento
        ads_automatic = self.env['xdocuments.comercial.ads'].search([('active', '=', True)
                                                    , ('automatic_apply', '=', True), ('destination_type', 'in', (destination_type, destination_type2))
                                                    , ('date_from', '<=', document_date), ('date_to', '>=', document_date)
                                                    , '|', ('partner_type', '=', 'all'), ('is_foreign', '=', partner_id.x_foreign_partner)], order='sequence')
        # Solo agrega los ads automáticos que no quita ads automáticos que son reemplados por uno específico del partner
        for ads in ads_automatic:
            if not ads_partner.filtered(lambda a: a.automatic_ads_replaced_id.id == ads.id):
                ads_list.append({'orden': ads.sequence, 'id': ads.id, 'data': ads.data})

        # Agrega los ads propios del contacto
        ads_list += [{'orden': ads.sequence, 'id': ads.id, 'data': ads.data} for ads in ads_partner]

        if ads_list:
            ads_list = sorted(ads_list, key=lambda r: r.get('orden',1) )
        return ads_list
