# Part of RU3IX licensing
# See __manifest__.py file for full copyright and licensing details.

#pylint: disable=too-few-public-methods,import-error,invalid-name
""" Hr Payslip Run Inherit """

from datetime import datetime
import operator
import itertools
from odoo import fields, models
from collections import OrderedDict


class HrPayslipRun(models.Model):
	""" HrPayslipRun Inherit """
	_inherit = "hr.payslip.run"

	def _get_spo_report_footer_date(self):
		date = datetime.now()
		date_today = date.strftime("%d %b %Y %H:%M %p")
		if date_today:
			date_today = date_today
		else:
			date_today = date
		return date_today


	def _get_spo_report_date_period(self):
		date_period = ''
		date_start = datetime.strptime(str(self.date_start), "%Y-%m-%d").strftime("%d %b %Y")
		date_end = datetime.strptime(str(self.date_end), "%Y-%m-%d").strftime("%d %b %Y")
		if date_start and date_end:
			date_period = str(date_start) + ' To ' + str(date_end)
		return date_period


	##### Payroll GL Report #####
	def _get_payroll_gl_report_lines(self):
		""" Employee Overtime Report Line """
		res = []
		total_basic_salary = 0.0
		total_taxation = 0.0
		total_superannuation = 0.0
		total_net_wages = 0.0
		if self.slip_ids:
			for slip in self.slip_ids:
				for line in slip.line_ids:
					if line.code == 'BASIC':  # Basic Salary
						total_basic_salary += line.total
					elif line.code == 'WITHHOLD.TOTAL':  # Taxation
						total_taxation += line.total
					elif line.code in ('SUPER_EMP','SUPER_EMP_ADD','SUPER'):  # Superannuation Fund
						total_superannuation += line.total
					elif line.code == 'NET':  # Net Wages
						total_net_wages += line.total

		return {
			'total_basic_salary': total_basic_salary,
			'total_taxation': total_taxation,
			'total_superannuation': total_superannuation,
			'total_net_wages': total_net_wages,
		}

	def _get_payroll_gl_report_dept_lines(self):
		""" Fetches Payroll GL Report Lines based on Salary Rules with enable_report=True """

		res = {}

		# Fetch all salary rules where enable_report=True
		# salary_rules = self.env['hr.salary.rule'].search([('enable_report', '=', True)])

		if self.slip_ids:
			for slip in self.slip_ids:
				for line in slip.line_ids.filtered(lambda line: line.salary_rule_id.enable_report == True):
					rule = line.salary_rule_id

					# Process only rules that have enable_report=True
					if rule and rule.enable_report:
						key = (rule.gl_desc, rule.gl_code)

						if key not in res:
							res[key] = {'rate': 0.0, 'gl_code': rule.gl_code, 'hours': 0.0}

						res[key]['rate'] += -abs(line.total)  # Aggregate total amount

		# Convert dictionary to list of dictionaries
		result = [{'gl_desc': key[0], 'rate': value['rate'], 'gl_code': value['gl_code'], 'hours': value['hours']} for
				  key, value in res.items()]

		return result

	def get_department_wise_payroll_report(self):
		"""
		Generate a department-wise payroll report that includes only departments
		with enabled GL reports and payslips in the given batch. The report aggregates
		the sum of each salary rule per department.
		"""
		report_data = {}

		# Get only departments with enabled GL reports
		departments = self.env['hr.department'].search([('enable_report', '=', True)])

		for dept in departments:
			# Fetch payslips in the given batch that belong to this department
			payslips = self.slip_ids.filtered(lambda rl: rl.employee_id.department_id.id == dept.id)

			if not payslips:
				continue  # Skip departments without payslips in this batch

			for payslip in payslips:
				for slip_line in dept.salary_rule_ids:
					for line in payslip.line_ids.filtered(lambda rl: rl.salary_rule_id.code == slip_line.rule_id.code):
						key = (f"{dept.name + '/' + slip_line.gl_desc}", slip_line.gl_code)
						if key not in report_data:
							report_data[key] = {'rate': 0.0, 'hours': 0.0}
						report_data[key]['rate'] += line.total

				for work_line in dept.work_type_ids:
					for line in payslip.worked_days_line_ids.filtered(
							lambda rl: rl.work_entry_type_id.id == work_line.work_entry_type_id.id):
						key = (f"{dept.name + '/' +work_line.gl_desc}", work_line.gl_code)
						if key not in report_data:
							report_data[key] = {'rate': 0.0, 'hours': 0.0}
						report_data[key]['rate'] += line.amount
						report_data[key]['hours'] += line.number_of_hours

				for input_line in dept.input_type_ids:
					for line in payslip.input_line_ids.filtered(
							lambda rl: rl.input_type_id.code == input_line.input_type_id.code):
						key = (f"{dept.name + '/' + input_line.gl_desc}", input_line.gl_code)
						if key not in report_data:
							report_data[key] = {'rate': 0.0, 'hours': 0.0}
						report_data[key]['rate'] += line.amount

		# Convert dictionary to a structured list
		result = [{'gl_description': key[0], 'gl_code': key[1], 'rate': value['rate'], 'hours': value['hours']}
				  for key, value in report_data.items()]

		return result


