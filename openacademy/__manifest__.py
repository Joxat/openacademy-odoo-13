{
    'name': 'Odoo Courses',
    'version': '13.00',
    'description': """
    - training courses
    - training session
    - training registration
    """,
    'category': 'just for testing',
    'Author': 'Mohammed',
    'website': 'www.google.com',
    'depends': ['base', 'sale', 'mail', 'report_xlsx'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/openacademy.xml',
        'views/partner.xml',
        'reports/paperformat.xml',
        'reports/report.xml',
        'reports/sale_qweb_inherit.xml',
        'wizard/wizard.xml',
        'views/oa_wizard_pdf.xml',
        'data/email_template.xml',
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'views/res_config_settings.xml',
        'views/template.xml',
        'reports/reportat.xml',
        


    ],
    'demo': [],
}
