# -*- coding: utf-8 -*-
{
    'name': 'xoverdue bills',
    'summary': 'Advierte sobre Facturas Vencidas de un cliente',
    'description': """
        Indica al usuario mediente un mensaje cuando un cliente tiene
        facturas Vencidas al facturar o realizar un presupuesto.
    """,
    'author': '`Prointec',
    'category': 'Sales',
    'version': '14.0.0.1',
    'depends': ["base", "sale", "account", ],
'data': [
        'views/sale_account_invoice_views.xml',
        'views/sale_order_views.xml',
        'views/pos_order_invoice.xml',
    ],
}
