from odoo import models, fields, api
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(string='Mã nhân viên',copy=False)
    education_level = fields.Selection([
        ('high_school', 'Trung học phổ thông'),
        ('college', 'Cao đẳng'),
        ('university', 'Đại học'),
        ('master', 'Thạc sĩ'),
        ('doctor', 'Tiến sĩ'),
    ], string='Trình độ học vấn')

    work_location = fields.Char(string='Địa điểm làm việc')