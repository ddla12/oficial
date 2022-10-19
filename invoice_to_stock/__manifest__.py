# -*- coding: utf-8 -*-
{
    'name': "xInvoice to Stock",
    'version': '14.0',
    'category': 'Accounting',
    'summary': """Genera el movimiento de inventario a partir de una nota de crédito""",
    "description": """
    """,
    'website': "http://www.prointeccr.com",
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'sale', 'stock', 'sale_stock'],
    'data': [
        'views/invoice_stock_view.xml',
        'wizards/account_move_reverse_view.xml',
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
