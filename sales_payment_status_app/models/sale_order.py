# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models, _
from odoo.tools import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_status = fields.Selection([('no_invoice', 'No Invoice'), ('not_paid', 'Not Paid'),
                                       ('partially_paid', 'Partially Paid'), ('overdue', 'Overdue'),
                                       ('fully_paid', 'Fully Paid')],
                                      store=True, compute="compute_payment_status")
    amount_due = fields.Float(string="Amount Due", compute="compute_payment_status")

    sale_payment_details = fields.Binary(groups="account.group_account_invoice,account.group_account_readonly",
                                         exportable=False,
                                         compute='compute_sale_payment_details_info')
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string="Payment",
        index='btree_not_null',
        copy=False,
        check_company=True,
    )

    def js_remove_outstanding_partial(self, partial_id):
        ''' Called by the 'payment' widget to remove a reconciled entry to the present invoice.

        :param partial_id: The id of an existing partial reconciled with the current invoice.
        '''
        print(partial_id,'partial_id')
        self.ensure_one()
        partial = self.env['account.partial.reconcile'].browse(partial_id)
        return partial.unlink()

    def action_open_business_doc(self):
        self.ensure_one()
        invoice_id = self.env['account.move'].sudo().browse(self.id)
        print(invoice_id,'hhhhh')
        if invoice_id.payment_id:
            name = _("Payment")
            res_model = 'account.payment'
            res_id = invoice_id.payment_id.id
        elif invoice_id.statement_line_id:
            name = _("Bank Transaction")
            res_model = 'account.bank.statement.line'
            res_id = invoice_id.statement_line_id.id
        else:
            name = _("Journal Entry")
            res_model = 'account.move'
            res_id = invoice_id.id

        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': res_model,
            'res_id': res_id,
            'target': 'current',
        }

    # def action_open_business_doc(self):
    #     # self.ensure_one()
    #     if self.payment_id:
    #         name = _("Payment")
    #         res_model = 'account.payment'
    #         res_id = self.payment_id.id
    #     else:
    #         name = _("Journal Entry")
    #         res_model = 'account.move'
    #         res_id = self.invoice_ids[0].id
    #
    #     return {
    #         'name': name,
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'views': [(False, 'form')],
    #         'res_model': res_model,
    #         'res_id': res_id,
    #         'target': 'current',
    #     }

    # @api.depends('state', 'picking_ids.state', 'invoice_ids.state', 'invoice_ids.payment_state')
    def compute_payment_status(self):
        for rec in self:
            amount_due = 0
            if rec.invoice_ids:

                if any(d.payment_state == "partial" for d in rec.invoice_ids):
                    rec.payment_status = 'partially_paid'
                    amount_due = sum([line.amount_residual for line in rec.invoice_ids])

                if all(d.payment_state == "paid" for d in rec.invoice_ids):
                    amount_due = 0.00
                    rec.payment_status = 'fully_paid'
                else:
                    if all(d.state == "posted" for d in rec.invoice_ids):
                        if any(d.payment_state in ["partial", 'not_paid', 'paid'] for d in rec.invoice_ids):
                            rec.payment_status = 'partially_paid'
                        if any(d.invoice_date_due < date.today() for d in rec.invoice_ids):
                            rec.payment_status = 'overdue'
                    amount_due = sum([line.amount_residual for line in rec.invoice_ids])
                if all(d.payment_state == "not_paid" for d in rec.invoice_ids):
                    rec.payment_status = 'not_paid'
                    amount_due = sum([line.amount_total for line in rec.invoice_ids])

            else:
                rec.payment_status = 'no_invoice'
                amount_due = 0.00
            rec.amount_due = amount_due

    def action_payment_register(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'sale.register.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('invoice_ids.move_type', 'invoice_ids.line_ids.amount_residual')
    def compute_sale_payment_details_info(self):
        for rec in self:
            rec.sale_payment_details = False
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            for move in rec.invoice_ids:
                if move.state == 'posted' and move.is_invoice(include_receipts=True):
                    reconciled_vals = []
                    reconciled_partials =  move._get_all_reconciled_invoice_partials()
                    print('REEE',reconciled_partials)
                    for reconciled_partial in reconciled_partials:
                        counterpart_line = reconciled_partial['aml']
                        if counterpart_line.move_id.ref:
                            reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                        else:
                            reconciliation_ref = counterpart_line.move_id.name
                        if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                            foreign_currency = counterpart_line.currency_id
                        else:
                            foreign_currency = False

                        reconciled_vals.append({
                            'name': counterpart_line.name,
                            'journal_name': counterpart_line.journal_id.name,
                            'amount': reconciled_partial['amount'],
                            'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
                            reconciled_partial['currency'].id,
                            'date': counterpart_line.date,
                            'partial_id': reconciled_partial['partial_id'],
                            'account_payment_id': counterpart_line.payment_id.id,
                            'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                            'move_id': counterpart_line.move_id.id,
                            'memo': reconciliation_ref,
                            # these are necessary for the views to change depending on the values
                            'is_exchange': reconciled_partial['is_exchange'],
                            'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
                                                                  currency_obj=counterpart_line.company_id.currency_id),
                            'amount_foreign_currency': foreign_currency and formatLang(self.env,
                                                                                       abs(counterpart_line.amount_currency),
                                                                                       currency_obj=foreign_currency)
                        })
                    payments_widget_vals['content'] = reconciled_vals
                print(payments_widget_vals['content'])
                if payments_widget_vals['content']:
                    rec.sale_payment_details = payments_widget_vals
                else:
                    rec.sale_payment_details = False


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
