# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Payment Status',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Track payment status of sales orders and register payments',
    'description': """
        This module adds payment status tracking to sales orders:
        - Payment status field showing: No Invoice, Not Paid, Partially Paid, Fully Paid, Overdue
        - Register payment button to create payments directly from sale order
        - Payment status filters in sale order list view
        - Automatic status updates based on invoice payment states
    """,
    'author': 'DevHost',
    'website': 'https://www.devhost.io',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_payment_wizard_view.xml',
        'views/sale_order_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
