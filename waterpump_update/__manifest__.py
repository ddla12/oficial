# -*- coding: utf-8 -*-
{
    'name': "water pump update",
    'summary': """
        Modulo que se encarga de las modificasiones personalizadas de water pump
    """,
    'description': """
        +mueve el campo de ref interna a un lugar mas visible
    """,
    'category': 'Extra',
    'version': '14',
    'author': "PROINTEC",
    'website': "http://www.prointeccr.com",
    'depends': ['base', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
    ],
}
