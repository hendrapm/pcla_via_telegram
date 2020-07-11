# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
import requests
import logging


class SendApproval(models.TransientModel):
    _name = 'send.approval'
    _description = 'Send Approval'

    sale_ids = fields.Many2many('sale.order', 'sale_order_send_approval_rel')

    def send_approval_request(self):
        telegram_api_url = self.env['ir.config_parameter'].sudo().get_param('partner_credit_limit.telegram_api_url')
        token_bot = self.env['ir.config_parameter'].sudo().get_param('partner_credit_limit.telegram_bot_token')
        if not token_bot:
            raise UserError(_('please fill token bot parameter'))
        url = os.path.join(telegram_api_url, 'bot{token}'.format(token=token_bot))
        userid1 = self.env['ir.config_parameter'].sudo().get_param('partner_credit_limit.telegram_userid1')
        if str(userid1).isdigit():
            userid1 = int(userid1)
        else:
            raise UserError(_('userid parameter should be digit'))
        sale_id = self.sale_ids[0]
        message = """
Dear Credit Limit Approver,

Customer berikut ini :
Nama                    = %s
Credit limit           = %s
Over credit limit  = %s

mohon approvalnya untuk merilis SO %s dengan jumlah %s
            """ % (sale_id.partner_id.display_name, sale_id.partner_id.credit_limit, abs(self._context.get('available_credit_limit')), sale_id.name, sale_id.amount_total)
        data = {
            'chat_id': userid1,
            'text': message,
            'reply_markup': {
                'inline_keyboard': [
                    [{'text': 'Approve', 'callback_data': 't|%s' % sale_id.id},
                    {'text': 'Reject', 'callback_data': 'f|%s' % sale_id.id}]
                ]
            }
        }
        resp = requests.post(url + '/sendMessage', json=data)
        if not resp.ok:
            raise UserError(_(resp.text))
        sale_id.state = 'waiting'
        return True

