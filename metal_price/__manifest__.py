# -*- coding: utf-8 -*-
{
    'name': "Metal Price",
    'summary': """
        Metal Price Determining in invoice
        
    """,
    'description': """
        This module is used to determine metal price with different unit of measure 
    """,
    'author': "Abdelrhman Ashraf",
    'website': "https://www.yourcompany.com",
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/metal_price_views.xml',
        'views/partner_view.xml',
    ],
    'category': 'Accounting/Accounting',
    'version': "16.0.0.0.1",
    'support': 'abdelrhmanmano7@gmail.com',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['base', 'account', 'uom'],
}
