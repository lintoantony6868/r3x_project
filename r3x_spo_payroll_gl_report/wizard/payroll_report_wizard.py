# Part of RU3IX licensing
# See __manifest__.py file for full copyright and licensing details.

from datetime import datetime
import operator
import itertools
from odoo import fields, api, models



class payroll_gl_report_wizard(models.TransientModel):
	_name = "payroll.gl.report.wizard"
	_description = 'Payroll GL Report Wizard'

	group_by = fields.Boolean('Group By ?', default=True)

	def print_report_pdf(self):
		datas = {}
		context = self.env.context.copy()
		docids = self.env.context.get('active_ids', [])
		if self.group_by:
			datas.update({
				'active_ids': docids,
			})
			return self.env.ref('r3x_spo_payroll_gl_report.action_report_payroll_gl_group').report_action(docids, data=datas)
		else:
			return self.env.ref('r3x_spo_payroll_gl_report.action_report_payroll_gl').report_action(docids, data=datas)
	def print_report_xlxs(self):
		datas = {}
		context = self.env.context.copy()
		docids = self.env.context.get('active_ids', [])
		if self.group_by:
			datas.update({
				'active_ids': docids,
			})
			return self.env.ref('r3x_spo_payroll_gl_report.action_report_payroll_gl_excel_group').report_action(docids, data=datas)
		else:
			return self.env.ref('r3x_spo_payroll_gl_report.action_report_payroll_gl_excel').report_action(docids,
																										  data=datas)

