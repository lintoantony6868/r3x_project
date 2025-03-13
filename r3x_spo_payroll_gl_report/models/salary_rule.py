from odoo import api, fields, models, _


class HrSalaryRule(models.Model):
	_inherit = "hr.salary.rule"

	enable_report = fields.Boolean(string="View on GL Report.?")
	gl_code = fields.Char(string="GL Code")
	gl_desc = fields.Char(string="GL Description")
