from odoo import models, fields, api

class SalaryRuleWizard(models.TransientModel):
    _name = 'salary.rule.wizard'
    _description = 'Salary Rule Selection Wizard'

    department_id = fields.Many2one('hr.department', string="Department", required=True)
    rule_ids = fields.Many2many('hr.salary.rule', string="Select Salary Rules")
    work_entry_type_ids = fields.Many2many('hr.work.entry.type', string="Select Work Entry Type")
    input_type_ids = fields.Many2many('hr.payslip.input.type', string="Select Work Entry Type")
    type = fields.Selection([
        ('rule', 'Salary Rule'),
        ('work_entry_type', 'Work Etry Type'),
        ('input_type', 'Work Etry Type'),
    ],)


    def action_add_multiple(self):
        if self.type == 'rule':
            for rule in self.rule_ids:
                self.env['salary.rule.report'].create({
                    'department_id': self.department_id.id,
                    'rule_id': rule.id,
                })
        elif self.type == 'work_entry_type':
            for we in self.work_entry_type_ids:
                self.env['work.entry.report'].create({
                    'department_id': self.department_id.id,
                    'work_entry_type_id': we.id,
                })
        elif self.type == 'input_type':
            for we in self.input_type_ids:
                self.env['input.type.report'].create({
                    'department_id': self.department_id.id,
                    'input_type_id': we.id,
                })

