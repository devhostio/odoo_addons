# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SaleRegisterPayment(models.TransientModel):
    _name = 'sale.register.payment'
    _description = "Sale Register Payment"

    sale_id = fields.Many2one('sale.order', string="Name")
    journal_id = fields.Many2one('account.journal', string="Payment", domain=[('type', 'in', ['bank', 'cash'])],
                                 required=True)
    partner_bank_id = fields.Many2one(comodel_name='res.partner.bank', string="Recipient Bank Account",
                                      readonly=False, store=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id',
                                 string='Company', readonly=True)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string='Currency', store=True, readonly=False)
    amount = fields.Monetary(currency_field='currency_id', string='Total Amount',
                             compute='compute_total_amount', store=True)
    register_line_ids = fields.One2many('sale.register.payment.line', 'register_id', 'Register Line')
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today)

    @api.depends('register_line_ids.amount')
    def compute_total_amount(self):
        for rec in self:
            rec.amount = sum([line.amount for line in rec.register_line_ids])

    @api.model
    def default_get(self, fields):
        res = super(SaleRegisterPayment, self).default_get(fields)
        sale_id = self.env['sale.order'].browse(self._context.get('active_id'))
        line_vals = []
        for invoice_id in sale_id.invoice_ids:
            line_vals.append(((0, 0, {
                'communication': invoice_id.name,
                'amount_residual': invoice_id.amount_residual,
                'amount': invoice_id.amount_residual,
                'invoice_id': invoice_id.id,
            })))
        res.update({
            'register_line_ids': line_vals,
            'sale_id': sale_id.id,
        })
        if 'journal_id' not in res:
            res['journal_id'] = self.env['account.journal'].search(
                [('company_id', '=', self.env.user.company_id.id), ('type', 'in', ('bank', 'cash'))], limit=1).id

        return res

    def action_create_payment(self):
        for rec in self:
            if rec.amount > 0:
                for line_id in self.register_line_ids:
                    if line_id.amount > 0:
                        payment_data = {
                            'currency_id': rec.currency_id.id,
                            'sale_order_id': rec.sale_id.id,
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'partner_id': rec.sale_id.partner_id.id,
                            'amount': line_id.amount,
                            'journal_id': rec.journal_id.id,
                            'date': rec.payment_date,
                            'ref': line_id.communication,
                        }
                        account_payment_id = self.env['account.payment'].create(payment_data)
                        account_payment_id.action_post()
                        domain = [('reconciled', '=', False)] #('account_type', 'in', ('receivable', 'payable')),
                        lines = line_id.invoice_id.line_ids
                        payment_lines = account_payment_id.line_ids.filtered_domain(domain)
                        for account in payment_lines.account_id:
                            (payment_lines + lines) \
                                .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                                .reconcile()
            else:
                raise ValidationError('Total amount should be greater then 0....')


class SaleRegisterPaymentLone(models.TransientModel):
    _name = 'sale.register.payment.line'
    _description = "Sale Register Payment Line"

    register_id = fields.Many2one('sale.register.payment', string='Register')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    currency_id = fields.Many2one('res.currency', related='register_id.currency_id', string='Currency', store=True,
                                  readonly=False)
    amount_residual = fields.Monetary(currency_field='currency_id', string='Due Amount', store=True, readonly=False)
    amount = fields.Monetary(currency_field='currency_id', string='Payment Amount', store=True, readonly=False)
    communication = fields.Char(string="Memo", store=True, readonly=False)
    payment_difference = fields.Monetary(compute="_compute_payment_difference")

    @api.depends('amount')
    def _compute_payment_difference(self):
        for rec in self:
            if rec.invoice_id:
                rec.payment_difference = rec.invoice_id.amount_residual - rec.amount
            else:
                rec.payment_difference = rec.amount
