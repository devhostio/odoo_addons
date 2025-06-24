# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_status = fields.Selection([
        ('no_invoice', 'No Invoice'),
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
    ], string='Payment Status', compute='_compute_payment_status', store=True, readonly=True)

    @api.depends('invoice_ids', 'invoice_ids.payment_state', 'invoice_ids.invoice_date_due')
    def _compute_payment_status(self):
        for order in self:
            if not order.invoice_ids:
                order.payment_status = 'no_invoice'
            else:
                # Filter out cancelled invoices
                valid_invoices = order.invoice_ids.filtered(lambda inv: inv.state != 'cancel')
                
                if not valid_invoices:
                    order.payment_status = 'no_invoice'
                    continue
                
                # Check for overdue invoices
                today = date.today()
                overdue_invoices = valid_invoices.filtered(
                    lambda inv: inv.payment_state != 'paid' and 
                    inv.invoice_date_due and 
                    inv.invoice_date_due < today
                )
                
                if overdue_invoices:
                    order.payment_status = 'overdue'
                    continue
                
                # Check payment states
                all_paid = all(inv.payment_state == 'paid' for inv in valid_invoices)
                any_paid = any(inv.payment_state in ['paid', 'in_payment', 'partial'] for inv in valid_invoices)
                any_partial = any(inv.payment_state in ['partial', 'in_payment'] for inv in valid_invoices)
                
                if all_paid:
                    order.payment_status = 'paid'
                elif any_partial or (any_paid and not all_paid):
                    order.payment_status = 'partial'
                else:
                    order.payment_status = 'not_paid'

    def action_register_payment(self):
        """Open payment wizard for the sale order's invoices"""
        self.ensure_one()
        
        # Get unpaid invoices
        unpaid_invoices = self.invoice_ids.filtered(
            lambda inv: inv.state == 'posted' and inv.payment_state != 'paid'
        )
        
        if not unpaid_invoices:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No unpaid invoices',
                    'message': 'There are no unpaid invoices for this sale order.',
                    'type': 'warning',
                }
            }
        
        return {
            'name': 'Register Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_invoice_ids': [(6, 0, unpaid_invoices.ids)],
                'default_partner_id': self.partner_id.id,
                'default_amount': sum(unpaid_invoices.mapped('amount_residual')),
            }
        }
