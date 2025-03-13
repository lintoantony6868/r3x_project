# Copyright Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

{
    'name': 'Payroll GL Report',
    'summary': 'Payroll GL Report',
    'version': '17.0.0.5',
    'author': 'RU3IX PTY LTD',
    'license': 'LGPL-3',
    'category' : 'Payroll',
    'depends': [
        'hr','hr_payroll'

    ],
    'data': [
        'security/ir.model.access.csv',
        'views/department_view.xml',
        'views/salary_rule_view.xml',
        'report/payroll_gl_report_templates.xml',
        'report/payroll_gl_report.xml',
        'wizard/payroll_report_wizard_view.xml',
        'wizard/multiple_select_wizard_view.xml',
    ],
    'images': '/static/description/icon.png',
    'application': True,
    'description': 'Payroll GL Report',
}
