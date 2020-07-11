{
    'name': 'Partner Credit Limit Approval Via Telegram',
    'version': '11.0.1.0.0',
    'category': 'Sale Approval',
    'license': '',
    'author': 'Hendra',
    'website': '',
    'maintainer': 'Hendra',
    'summary': 'approval via telegram in module partner_credit_limit',
    'depends': [
        'partner_credit_limit',
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'wizard/confirmation_dialog.xml',
        'views/sale_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
