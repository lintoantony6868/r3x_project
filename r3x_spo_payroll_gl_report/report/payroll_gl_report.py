# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools import format_date, frozendict
from datetime import datetime, date



class report_payroll_gl_report_group(models.AbstractModel):
	""" Report Superannuation Payments - Group"""
	_name = 'report.r3x_spo_payroll_gl_report.report_payroll_gl_group'
	_description = "Payroll GL Group report"

	def _get_payroll_gl_report_lines(self, docids):
		res = []
		aggregated_data = {}
		batch_ids = self.env['hr.payslip.run'].browse(docids)

		if batch_ids:
			for batch in batch_ids:
				get_lines = batch._get_payroll_gl_report_dept_lines()
				res.extend(get_lines)
		if res:
			for entry in res:

				key = (entry['gl_desc'], entry['gl_code'])  # Unique key based on description and GL code
				if key not in aggregated_data:
					aggregated_data[key] = {'gl_desc': entry['gl_desc'], 'gl_code': entry['gl_code'], 'rate': 0.0,
											'hours': 0.0}

				aggregated_data[key]['rate'] += entry['rate']
				aggregated_data[key]['hours'] += entry['hours']

		return list(aggregated_data.values())
	def _get_payroll_gl_report_dept_lines(self, docids):
		res = []
		aggregated_data = {}
		batch_ids = self.env['hr.payslip.run'].browse(docids)

		if batch_ids:
			for batch in batch_ids:
				get_lines = batch.get_department_wise_payroll_report()
				res.extend(get_lines)

		if res:
			for entry in res:
				key = (entry['gl_description'], entry['gl_code'])  # Unique key based on description and GL code
				if key not in aggregated_data:
					aggregated_data[key] = {'gl_description': entry['gl_description'], 'gl_code': entry['gl_code'], 'rate': 0.0,
											'hours': 0.0}

				aggregated_data[key]['rate'] += entry['rate']
				aggregated_data[key]['hours'] += entry['hours']

		return list(aggregated_data.values())

	def _get_emp_overtime_report_footer_date(self):
		date = datetime.now()
		date_today = date.strftime("%d %b %Y %H:%M %p")
		if date_today:
			date_today = date_today
		else:
			date_today = date
		return date_today

	def get_payroll_gl_report_group_date(self,docids):
		batch_ids = self.env['hr.payslip.run'].browse(docids)
		date_string = []
		date_period = ''
		if batch_ids:
			for l in batch_ids:
				date_string.append(l.date_start)
				date_string.append(l.date_end)
			if date_string:
				min_date = min(date_string)
				max_date = max(date_string)
				date_start = datetime.strptime(str(min_date), "%Y-%m-%d").strftime("%d %b %Y")
				date_end = datetime.strptime(str(max_date), "%Y-%m-%d").strftime("%d %b %Y")
				if date_start and date_end:
					date_period = str(date_start) + ' To ' + str(date_end)
		return date_period

	def get_payroll_gl_report_group_end_date(self,docids):
		batch_ids = self.env['hr.payslip.run'].browse(docids)
		date_string = []
		date_period = ''
		if batch_ids:
			for l in batch_ids:
				date_string.append(l.date_end)
			if date_string:
				max_date = max(date_string)
				date_end = datetime.strptime(str(max_date), "%Y-%m-%d").strftime("%d/%m/%Y")
				if date_end:
					date_end = str(date_end)
		return date_end

	def _get_report_values(self, docids, data=None):
		wiz_id = data['context']['active_id']
		docs = self.env['payroll.report.wizard'].browse(wiz_id)
		active_ids = data['active_ids']
		get_report_lines = self._get_payroll_gl_report_lines(active_ids)
		get_report_dept_lines = self._get_payroll_gl_report_dept_lines(active_ids)
		get_report_date = self.get_payroll_gl_report_group_date(active_ids)
		get_report_end_date = self.get_payroll_gl_report_group_end_date(active_ids)
		return {
			'doc_ids': docs.ids,
			'doc_model': 'payroll.report.wizard',
			'docs': docs,
			'form': {
				'get_report_lines': get_report_lines,
				'get_report_date': get_report_date,
				'get_report_dept_lines': get_report_dept_lines,
				'get_report_footer_date': self._get_emp_overtime_report_footer_date(),
				'get_report_end_date': get_report_end_date,
			}
		}

