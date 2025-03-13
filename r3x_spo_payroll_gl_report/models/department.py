from odoo import api, fields, models, _


class HrDepartment(models.Model):
	_inherit = "hr.department"

	enable_report = fields.Boolean(string="Enable GL Report.?")
	salary_rule_ids = fields.One2many('salary.rule.report','department_id',string="Salary Rules")
	work_type_ids = fields.One2many('work.entry.report','department_id',string="Work Entry Types")
	input_type_ids = fields.One2many('input.type.report','department_id',string="Input Types")

	def action_open_salary_rule_wizard(self):
		"""Opens the wizard for selecting salary rules."""
		return {
			'name': 'Select Salary Rules',
			'type': 'ir.actions.act_window',
			'res_model': 'salary.rule.wizard',
			'view_mode': 'form',
			'view_id': self.env.ref('r3x_spo_payroll_gl_report.view_salary_rule_wizard_form').id,
			'target': 'new',
			'context': {'default_department_id': self.id,'default_type':'rule'},
		}
	def action_open_work_type_wizard(self):
		"""Opens the wizard for selecting salary rules."""
		return {
			'name': 'Select Work Entry Types',
			'type': 'ir.actions.act_window',
			'res_model': 'salary.rule.wizard',
			'view_mode': 'form',
			'view_id': self.env.ref('r3x_spo_payroll_gl_report.view_salary_rule_wizard_form').id,
			'target': 'new',
			'context': {'default_department_id': self.id,'default_type':'work_entry_type'},
		}
	def action_open_input_type_wizard(self):
		"""Opens the wizard for selecting salary rules."""
		return {
			'name': 'Select Work Entry Types',
			'type': 'ir.actions.act_window',
			'res_model': 'salary.rule.wizard',
			'view_mode': 'form',
			'view_id': self.env.ref('r3x_spo_payroll_gl_report.view_salary_rule_wizard_form').id,
			'target': 'new',
			'context': {'default_department_id': self.id,'default_type':'input_type'},
		}


class SalaryRuleReport(models.Model):
	_name = "salary.rule.report"

	department_id = fields.Many2one('hr.department',string="Department")
	rule_id = fields.Many2one('hr.salary.rule',string="Salary Rule")
	name = fields.Char(string="name")
	gl_code = fields.Char(string="GL Code")
	gl_desc = fields.Char(string="GL Description")

class WorkEntryReport(models.Model):
	_name = "work.entry.report"

	department_id = fields.Many2one('hr.department',string="Department")
	work_entry_type_id = fields.Many2one('hr.work.entry.type',string="Work Entry Type")
	name = fields.Char(string="name")
	gl_code = fields.Char(string="GL Code")
	gl_desc = fields.Char(string="GL Description")

class InputTypeReport(models.Model):
	_name = "input.type.report"

	name = fields.Char(string="name")
	department_id = fields.Many2one('hr.department',string="Department")
	input_type_id = fields.Many2one('hr.payslip.input.type',string="Other Input Type")
	gl_code = fields.Char(string="GL Code")
	gl_desc = fields.Char(string="GL Description")
