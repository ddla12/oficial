# -*- coding: utf-8 -*-
{
    'name': "xWaterPump sale update",
    'summary': """Actualización de ventas para WaterPump""",
    'description': """
        Modificaciones personalizadas para WaterPump
        + evita que la fecha pueda ser modificada        
        + Muestra los picking en el módulo de facturación
""",
    'category': 'Extra',
    'version': '14',
    'author': "PROINTEC",
    'website': "http://www.prointeccr.com",
    'license': 'LGPL-3',
    'depends': ['base', 'FAE_app', 'pos_extensionfe', 'purchase', 'stock_account'],
    'data': [
        'views/account_move_views.xml',
        'views/pos_order_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'report/pos_order_invoice_template.xml',
    ],
}
