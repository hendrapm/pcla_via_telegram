# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('waiting', 'Waiting for Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def check_limit(self):
        self.ensure_one()
        if self._context.get('bypass_check_limit'):
            return True
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.user_type_id.name', 'in', ['Receivable']),
             ('amount_residual', '>', 0)            
            ]
        )
        confirm_sale_order = self.search([('partner_id', '=', partner.id), ('state', '=', 'sale')])
        debit, credit = 0.0, 0.0
        amount_total = 0.0
        for status in confirm_sale_order:
            amount_total += status.amount_total
        for line in movelines:
            credit += line.credit
            debit += line.debit
        partner_credit_limit = (partner.credit_limit - debit) + credit
        available_credit_limit = ((partner_credit_limit - (amount_total - debit)) + self.amount_total)

        msg = False
        if (amount_total - debit) > partner_credit_limit:
            if not partner.over_credit:
                msg = 'You can not confirm Sale Order. <br/> Your available credit limit'\
                      ' Amount = %s <br/>Check "%s" Accounts or Credit ' \
                      'Limits.' % (available_credit_limit,
                                   self.partner_id.name)
            partner.write({'credit_limit': credit - debit + self.amount_total})
        
        if not msg:
            return True
        
        view = self.env.ref('pcla_via_telegram.view_send_approval')
        view.arch = view.arch.replace('replace_me_please', msg)
        wiz = self.env['send.approval'].create({'sale_ids': [(4, s.id) for s in self]})
        return {
            'name': _('Credit Limit Approval'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'send.approval',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': dict(self.env.context, available_credit_limit=available_credit_limit),
        }

    @api.multi
    def confirm_sale(self):
        for order in self:
            res = order.check_limit()
            if isinstance(res, dict):
                return res
        return self.action_confirm()

    def process_sale_order(self, approve):
        if approve:
            return self.with_context({'bypass_check_limit': True}).action_confirm()
        else:
            return self.action_cancel()
        
