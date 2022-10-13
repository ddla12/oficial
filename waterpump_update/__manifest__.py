# -*- coding: utf-8 -*-
{
    'name': "water pump update",

    'summary': """
        Modulo que se encarga de las modificasiones personalizadas de water pump
    """,

    'description': """
        -evita que la fecha pueda ser modificada
        -mueve el campo de ref interna a un lugar mas visible
    """,

    'author': "PROINTEC",
    'website': "http://www.prointeccr.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'contacts', 'FAE_app', 'pos_extensionfe', 'purchase'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'report/pos_order_invoice_template.xml',
    ],
}
