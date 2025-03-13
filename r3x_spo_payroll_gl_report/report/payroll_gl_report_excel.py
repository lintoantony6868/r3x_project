from odoo import models
import io
import xlsxwriter
from datetime import datetime
from odoo.http import content_disposition, request


class PayrollGlReport(models.AbstractModel):
    _name = 'report.r3x_spo_payroll_gl_report.payroll_gl_report_xlxs'
    _inherit = "report.report_xlsx.abstract"
    _description = 'Payroll GL Excel Report'

    def _get_payroll_gl_report_dept_lines(self):
        """ Employee Overtime Report Line with Correct Headers """

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
                        key = (f"{dept.name + '/' + work_line.gl_desc}", work_line.gl_code)
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

    def generate_xlsx_report(self, workbook, data, objects):
        for obj in objects:
            row = 8  # Starting row for data
            sheet = workbook.add_worksheet('Payroll GL Report')

            # Formats
            currency_symbol = self.env.company.currency_id.symbol if self.env.company.currency_id else '$'
            header_format = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': 'black', 'font_color': 'white', 'font_size': 14})
            subheader_format = workbook.add_format({'bold': True, 'font_color': 'black', 'font_size': 12})
            cell_format = workbook.add_format({'align': 'left', 'font_size': 10, 'color': 'black'})
            cell_format_right = workbook.add_format(
                {'num_format': f'"{currency_symbol}"#,##0.00', 'align': 'right', 'font_size': 10, 'color': 'black'})
            cell_format_total = workbook.add_format(
                {'num_format': '#,##0.00', 'bold': True, 'align': 'right', 'font_size': 10, 'color': 'black'})
            cell_format_total_hrs = workbook.add_format(
                {'num_format': 'h:mm', 'bold': True, 'align': 'right', 'font_size': 10, 'color': 'black'})
            cell_format_indent = workbook.add_format({'align': 'left', 'indent': 1, 'font_size': 10, 'color': 'black'})
            cell_format_right_hrs = workbook.add_format(
                {'num_format': 'h:mm', 'align': 'right', 'font_size': 10, 'color': 'black'})
            currency_format = workbook.add_format({'num_format': '#,##0.00'})

            # Merging headers
            sheet.merge_range('A2:H3', 'Payroll GL Report', header_format)

            # Column sizes
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 50)
            sheet.set_column('C:H', 15)

            # Headers
            headers = ["Trans. Date", "Department / Account Description", "Account No.", "Value", "Hours"]
            for col, header in enumerate(headers):
                sheet.write(7, col, header, header_format)

            payroll_lines = obj._get_payroll_gl_report_dept_lines()
            department_wise_data = obj.get_department_wise_payroll_report()

            # Write Payroll GL lines
            row = 9
            start_row = row + 1  # To use in SUM formula later
            total_hours = 0.0
            total_amount = 0.0
            for line in payroll_lines:
                total_amount += line['rate']
                total_hours += line['hours']
                sheet.write(row, 0, obj.date_end.strftime('%d/%m/%Y'))
                sheet.write(row, 1, line['gl_desc'])
                sheet.write(row, 2, line['gl_code'])
                sheet.write(row, 3, line['rate'], cell_format_right)
                sheet.write(row, 4, line['hours'], cell_format_right_hrs)
                row += 1

            # Write Department-wise Payroll Data
            for line in department_wise_data:
                total_amount += line['rate']
                total_hours += line['hours']
                sheet.write(row, 0, obj .date_end.strftime('%d/%m/%Y'))
                sheet.write(row, 1, line['gl_description'])
                sheet.write(row, 2, line['gl_code'])
                sheet.write(row, 3, line['rate'], cell_format_right)
                sheet.write(row, 4, line['hours'], cell_format_right_hrs)
                row += 1

            end_row = row  # Last row for summing totals
            total_amount = round(total_amount, 2)
            total_hours = round(total_hours, 2)
            # Add total row
            sheet.write(row, 1, 'TOTAL', subheader_format)
            sheet.write(row, 3, str(total_amount), cell_format_total)  # Sum of "Rate" column
            sheet.write(row, 4, str(total_hours), cell_format_total_hrs)  # Sum of "Hours" column

class PayrollGlReportGroup(models.AbstractModel):
    _name = "report.r3x_spo_payroll_gl_report.payroll_gl_report_xlxs_group"
    _inherit = "report.report_xlsx.abstract"
    _description = "Payroll GL Report Group Excel"

    def float_to_excel_time(self, float_hours):
        return float_hours / 24

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
                    aggregated_data[key] = {'gl_description': entry['gl_description'], 'gl_code': entry['gl_code'],
                                            'rate': 0.0,
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

    def get_payroll_gl_report_group_date(self, docids):
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

    def get_payroll_gl_report_group_end_date(self, docids):
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

    def generate_xlsx_report(self, workbook, data, objects):
        batch_obj = self.env['hr.payslip.run']
        active_ids = data['active_ids']
        get_report_lines = self._get_payroll_gl_report_lines(active_ids)
        get_report_dept_lines = self._get_payroll_gl_report_dept_lines(active_ids)
        get_report_date = self.get_payroll_gl_report_group_date(active_ids)
        row_2 = 1
        sheet = workbook.add_worksheet('Payroll GL Report')
        currency_symbol = self.env.company.currency_id.symbol if self.env.company.currency_id else '$'
        cell_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': 'black', 'font_color': 'white', 'font_size': '10'})
        header_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': 'black', 'font_color': 'white', 'font_size': '10'})
        header2_format = workbook.add_format({'bold': True, 'font_color': 'black', 'font_size': '12'})
        cell_format_left = workbook.add_format({'align': 'left', 'font_size': '10', 'color': 'black'})
        cell_format_right = workbook.add_format(
            {'num_format': f'"{currency_symbol}"#,##0.00', 'align': 'right', 'font_size': '10', 'color': 'black'})
        cell_format_right_hrs = workbook.add_format(
            {'num_format': 'hh:mm', 'align': 'right', 'font_size': '10', 'color': 'black'})
        cell_format_total = workbook.add_format(
            {'num_format': f'"{currency_symbol}"#,##0.00', 'bold': True, 'align': 'right', 'font_size': '10',
             'color': 'black'})
        cell_format_total_hrs = workbook.add_format(
            {'num_format': 'hh:mm', 'bold': True, 'align': 'right', 'font_size': '10',
             'color': 'black'})
        subheader_format = workbook.add_format({'bold': True, 'font_color': 'black', 'font_size': 12})

        sheet.merge_range('A2:E3', 'Payroll GL Report', header_format)
        sheet.merge_range('B7:D7', 'PPE : ' + str(get_report_date), header2_format)

        sheet.set_column('A0:A9', 15)
        sheet.set_column('B0:B9', 50)
        sheet.set_column('C0:C9', 15)
        sheet.set_column('D0:D9', 15)
        sheet.set_column('E0:D9', 15)

        headers = ["Trans. Date", "Department / Account Description", "Account No.", "Value", "Hours"]
        for col, header in enumerate(headers):
            sheet.write(7, col, header, header_format)

        row = 9
        start_row = row + 1  # To use in SUM formula later
        total_hours = 0.0
        total_amount = 0.0
        for line in get_report_lines:
            total_hours += line['hours']
            total_amount += line['rate']
            sheet.write(row, 0, self.get_payroll_gl_report_group_end_date(active_ids))
            sheet.write(row, 1, line['gl_desc'])
            sheet.write(row, 2, line['gl_code'])
            sheet.write(row, 3, line['rate'], cell_format_right)
            sheet.write(row, 4, line['hours'], cell_format_right_hrs)
            row += 1

        # Write Department-wise Payroll Data
        for line in get_report_dept_lines:
            total_hours += line['hours']
            total_amount += line['rate']
            sheet.write(row, 0, self.get_payroll_gl_report_group_end_date(active_ids))
            sheet.write(row, 1, line['gl_description'])
            sheet.write(row, 2, line['gl_code'])
            sheet.write(row, 3, line['rate'], cell_format_right)
            sheet.write(row, 4, line['hours'], cell_format_right_hrs)
            row += 1

        end_row = row  # Last row for summing totals

        total_amount = round(total_amount,2)
        total_hours = round(total_hours,2)
        # Add total row
        sheet.write(row, 1, 'TOTAL', subheader_format)
        sheet.write(row, 3, str(total_amount), cell_format_total)  # Sum of "Rate" column
        sheet.write(row, 4, str(total_hours), cell_format_total_hrs)  # Sum of "Hours" column

    #

