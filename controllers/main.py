from odoo import http, api
from odoo.http import request
import logging
import json


class PartnerCreditLimitApprovalController(http.Controller):

    @http.route(['/api/credit_limit/approval'], type='json', auth='none', csrf=False, methods=['POST'])
    def update_grn_qty_done(self, **kwargs):
        if request.httprequest.method == 'POST':
            data = kwargs.get('data', '')
            approval_value, sale_id = data.split('|')
            env = api.Environment(request.cr, 1, request.context)
            sale_obj = env['sale.order'].browse(int(sale_id))
            if str(approval_value).strip().lower() == 't':
                sale_obj.process_sale_order(approve=True)
            else:
                sale_obj.process_sale_order(approve=False)
            return {'status': 'ok'}
        return {'status': 'failed'}