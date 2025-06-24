# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Payment Status | Invoice Payment Status | Customer Payment Details | Payment Status in Sales | Amount Due on Sale',
    "author": "Edge Technologies",
    'version': '18.0',
    'live_test_url': "https://youtu.be/89qjNtmcp-4",
    "images":['static/description/main_screenshot.png'], 
    'summary': 'Sales Order Payment Status in Invoice Partial Payment Status in Sale Order Amount Due Quotation Payment Status in Sale Payment Details Show Invoice Register Payment Sale Payment Status in Sales Overdue Payment Status Sale Amount Due Invoice Payment Details',
    'description': 'This app provide feature like user can see invoice status and invoice payment status in sale order and also user register payment in sale order and provide invoice status filter in tree view and user see payment details in sale order',
    'license': "OPL-1",
    'depends': ['base','sale_management','stock','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/register_payment_views.xml',
        'views/sale_order_views.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'price': 9,
    'currency': "EUR",
    'category': 'sales',
}
