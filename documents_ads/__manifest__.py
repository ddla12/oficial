# -*- coding: utf-8 -*-
{
    'name': "xDocuments Ads",
    'summary':
        """
        Permite agregar notas y anuncios a factura y cotización
        """,
    'version': '14.0',
    'category': 'Extra Tools',
    'author': "PROINTEC",
    'website': "http://www.prointeccr.com",
    'license': 'AGPL-3',
    'depends': ['base', 'contacts', 'FAE_app'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_invoice.xml',
        'report/report_sale.xml',
        'views/documents_comercial_ads_views.xml',
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
