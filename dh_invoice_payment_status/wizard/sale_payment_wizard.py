# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class SalePaymentWizard(models.TransientModel):
    _name = 'sale.payment.wizard'
    _description = 'Sale Order Payment Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    invoice_ids = fields.Many2many('account.move', string='Invoices')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ['bank', 'cash'])])
    payment_method_line_id = fields.Many2one('account.payment.method.line', 
                                             string='Payment Method', 
                                             domain="[('journal_id', '=', journal_id)]")
    memo = fields.Char(string='Memo')

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            # Get the first available inbound payment method
            payment_method_line = self.journal_id.inbound_payment_method_line_ids[:1]
            self.payment_method_line_id = payment_method_line

    def action_create_payment(self):
        """Create payment and reconcile with invoices"""
        self.ensure_one()
        
        if not self.invoice_ids:
            raise UserError("No invoices selected for payment.")
        
        if self.amount <= 0:
            raise UserError("Payment amount must be greater than zero.")
        
        # Create payment
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
        }
        
        # Add memo as payment reference if available
        if self.memo:
            payment_vals['payment_reference'] = self.memo
        
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        
        # Get the payment move line from the payment's journal entry
        payment_move_line = payment.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        
        # Get invoice move lines to reconcile
        invoice_move_lines = self.invoice_ids.mapped('line_ids').filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable') and not line.reconciled
        )
        
        # Reconcile payment with invoices
        if payment_move_line and invoice_move_lines:
            (payment_move_line | invoice_move_lines).reconcile()
        
        # Return action to refresh the sale order view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
