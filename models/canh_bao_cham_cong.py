from collections import defaultdict
from datetime import date, datetime, time

from odoo import api, fields, models


class HrAttendanceAlert(models.Model):
    _name = 'hr.attendance.alert'
    _description = 'Cảnh báo chấm công'
    _order = 'period_start desc, total_violation_minutes desc, employee_id'

    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, readonly=True)
    department_id = fields.Many2one(
        'hr.department',
        string='Phòng ban',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    period_start = fields.Date(string='Từ ngày', required=True, readonly=True)
    period_end = fields.Date(string='Đến ngày', required=True, readonly=True)
    late_count = fields.Integer(string='Số lần đi muộn', readonly=True)
    late_minutes = fields.Integer(string='Tổng phút đi muộn', readonly=True)
    early_leave_count = fields.Integer(string='Số lần về sớm', readonly=True)
    early_leave_minutes = fields.Integer(string='Tổng phút về sớm', readonly=True)
    total_violation_minutes = fields.Integer(string='Tổng phút vi phạm', compute='_compute_total_violation_minutes', store=True)
    risk_score = fields.Integer(string='Điểm rủi ro', readonly=True)
    risk_level = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
    ], string='Mức rủi ro', readonly=True)
    state = fields.Selection([
        ('new', 'Mới'),
        ('reminded', 'Đã nhắc nhở'),
        ('monitoring', 'Đang theo dõi'),
        ('resolved', 'Đã cải thiện'),
    ], string='Trạng thái', default='new', required=True)
    note = fields.Text(string='Ghi chú xử lý')

    _sql_constraints = [
        ('employee_period_unique', 'unique(employee_id, period_start, period_end)', 'Mỗi nhân viên chỉ có một cảnh báo cho một kỳ.'),
    ]

    @api.depends('late_minutes', 'early_leave_minutes')
    def _compute_total_violation_minutes(self):
        for alert in self:
            alert.total_violation_minutes = alert.late_minutes + alert.early_leave_minutes

    @api.model
    def _calculate_risk(self, values, policy):
        """Chấm điểm theo mức vượt ngưỡng của chính sách chấm công."""
        late_score = min(
            (
                values['late_count'] / policy.late_occurrence_threshold
                + values['late_minutes'] / policy.late_minutes_threshold
            ) / 2 * 100,
            100,
        )
        early_leave_score = min(
            (
                values['early_leave_count'] / policy.early_leave_occurrence_threshold
                + values['early_leave_minutes'] / policy.early_leave_minutes_threshold
            ) / 2 * 100,
            100,
        )
        risk_score = min(
            round(max(late_score, early_leave_score) + min(late_score, early_leave_score) * 0.3),
            100,
        )
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 35:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        return risk_score, risk_level
    @api.model
    def action_generate_alerts_by_period(self, period_start, period_end):
        """Tự động tạo/cập nhật cảnh báo chấm công theo một khoảng thời gian."""
        attendance_records = self.env['hr.attendance'].search([
            ('check_in', '>=', datetime.combine(period_start, time.min)),
            ('check_in', '<', datetime.combine(period_end, time.max)),
        ])

        statistics = defaultdict(lambda: {
            'late_count': 0,
            'late_minutes': 0,
            'early_leave_count': 0,
            'early_leave_minutes': 0,
        })

        for attendance in attendance_records:
            values = statistics[attendance.employee_id.id]

            if attendance.so_phut_di_muon > 0:
                values['late_count'] += 1
                values['late_minutes'] += attendance.so_phut_di_muon

            if attendance.so_phut_ve_som > 0:
                values['early_leave_count'] += 1
                values['early_leave_minutes'] += attendance.so_phut_ve_som

        created_count = 0
        updated_count = 0

        attendance_model = self.env['hr.attendance']

        for employee_id, values in statistics.items():
            employee = self.env['hr.employee'].browse(employee_id)

            policy = attendance_model._lay_chinh_sach_cham_cong(employee)

            if not policy:
                continue

            exceeds_threshold = (
                values['late_count'] >= policy.late_occurrence_threshold
                or values['late_minutes'] >= policy.late_minutes_threshold
                or values['early_leave_count'] >= policy.early_leave_occurrence_threshold
                or values['early_leave_minutes'] >= policy.early_leave_minutes_threshold
            )

            if not exceeds_threshold:
                continue

            risk_score, risk_level = self._calculate_risk(
                values,
                policy
            )

            alert_values = dict(
                values,
                employee_id=employee.id,
                period_start=period_start,
                period_end=period_end,
                risk_score=risk_score,
                risk_level=risk_level,
            )

            alert = self.search([
                ('employee_id', '=', employee.id),
                ('period_start', '=', period_start),
                ('period_end', '=', period_end),
            ], limit=1)

            if alert:
                alert.write(alert_values)
                updated_count += 1
            else:
                self.create(alert_values)
                created_count += 1

        return {
            'created': created_count,
            'updated': updated_count,
            'attendance_records': len(attendance_records),
            'period_start': period_start,
            'period_end': period_end,
        }

    @api.model
    def action_generate_current_month_alerts(self):
        today = fields.Date.context_today(self)
        period_start = today.replace(day=1)
        if period_start.month == 12:
            next_month = date(period_start.year + 1, 1, 1)
        else:
            next_month = date(period_start.year, period_start.month + 1, 1)
        period_end = next_month.fromordinal(next_month.toordinal() - 1)

        attendance_records = self.env['hr.attendance'].search([
            ('check_in', '>=', datetime.combine(period_start, time.min)),
            ('check_in', '<', datetime.combine(next_month, time.min)),
        ])
        statistics = defaultdict(lambda: {
            'late_count': 0, 'late_minutes': 0,
            'early_leave_count': 0, 'early_leave_minutes': 0,
        })
        for attendance in attendance_records:
            values = statistics[attendance.employee_id.id]
            if attendance.so_phut_di_muon > 0:
                values['late_count'] += 1
                values['late_minutes'] += attendance.so_phut_di_muon
            if attendance.so_phut_ve_som > 0:
                values['early_leave_count'] += 1
                values['early_leave_minutes'] += attendance.so_phut_ve_som

        attendance_model = self.env['hr.attendance']
        for employee_id, values in statistics.items():
            employee = self.env['hr.employee'].browse(employee_id)
            policy = attendance_model._lay_chinh_sach_cham_cong(employee)
            if not policy:
                continue
            exceeds_threshold = (
                values['late_count'] >= policy.late_occurrence_threshold
                or values['late_minutes'] >= policy.late_minutes_threshold
                or values['early_leave_count'] >= policy.early_leave_occurrence_threshold
                or values['early_leave_minutes'] >= policy.early_leave_minutes_threshold
            )
            if not exceeds_threshold:
                continue
            risk_score, risk_level = self._calculate_risk(values, policy)
            alert_values = dict(
                values,
                employee_id=employee.id,
                period_start=period_start,
                period_end=period_end,
                risk_score=risk_score,
                risk_level=risk_level,
            )
            alert = self.search([
                ('employee_id', '=', employee.id),
                ('period_start', '=', period_start),
                ('period_end', '=', period_end),
            ], limit=1)
            if alert:
                alert.write(alert_values)
            else:
                self.create(alert_values)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cảnh báo chấm công',
            'res_model': 'hr.attendance.alert',
            'view_mode': 'tree,form',
            'domain': [('period_start', '=', period_start), ('period_end', '=', period_end)],
        }

    @api.model
    def cron_generate_current_month_alerts(self):
        self.action_generate_current_month_alerts()
