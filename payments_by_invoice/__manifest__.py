# -*- coding: utf-8 -*-
{
    'name': "Payments by Invoice",
    'summary': """Vista de pagos por factura""",
    'description': """Agrega la vista de pagos por factura al módulo de Facturación""",
    'version': '14.0',
    'category': 'Accounting',
    'author': "PROINTEC",
    'website': "http://www.prointeccr.com",
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/xaccount_payment_reconciled_views.xml',
    ],
    'qweb': []
}
