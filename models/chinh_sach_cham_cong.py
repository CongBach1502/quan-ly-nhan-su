from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrAttendancePolicy(models.Model):
    _name = 'hr.attendance.policy'
    _description = 'Chính sách chấm công'
    _order = 'company_id, department_id, name'

    name = fields.Char(
        string='Tên chính sách',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        required=True,
        default=lambda self: self.env.company,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Phòng ban áp dụng',
        help='Để trống để dùng làm chính sách mặc định cho toàn công ty.',
    )
    start_hour = fields.Float(
        string='Giờ bắt đầu',
        required=True,
        default=8.0,
    )
    end_hour = fields.Float(
        string='Giờ kết thúc',
        required=True,
        default=17.0,
    )
    grace_minutes = fields.Integer(
        string='Thời gian ân hạn (phút)',
        default=0,
        help='Nhân viên chấm công trong khoảng ân hạn vẫn được tính là đúng giờ.',
    )
    required_work_hours = fields.Float(
        string='Số giờ làm tối thiểu',
        required=True,
        default=8.0,
        help='Số giờ làm thực tế tối thiểu trong một ngày, không tính thời gian nghỉ.',
    )
    late_occurrence_threshold = fields.Integer(string='Ngưỡng số lần đi muộn', default=3)
    late_minutes_threshold = fields.Integer(string='Ngưỡng tổng phút đi muộn', default=60)
    early_leave_occurrence_threshold = fields.Integer(string='Ngưỡng số lần về sớm', default=3)
    early_leave_minutes_threshold = fields.Integer(string='Ngưỡng tổng phút về sớm', default=60)
    active = fields.Boolean(
        string='Đang áp dụng',
        default=True,
    )
    note = fields.Text(string='Ghi chú')

    @api.constrains('start_hour', 'end_hour', 'required_work_hours')
    def _check_working_hours(self):
        for policy in self:
            if not 0 <= policy.start_hour < 24 or not 0 < policy.end_hour < 24:
                raise ValidationError(
                    _('Giờ bắt đầu và giờ kết thúc phải nằm trong khoảng từ 00:00 đến trước 24:00.')
                )
            if policy.end_hour <= policy.start_hour:
                raise ValidationError(
                    _('Giờ kết thúc phải sau giờ bắt đầu.')
                )
            if policy.required_work_hours <= 0:
                raise ValidationError(_('Số giờ làm tối thiểu phải lớn hơn 0.'))
            if policy.required_work_hours > policy.end_hour - policy.start_hour:
                raise ValidationError(
                    _('Số giờ làm tối thiểu không được lớn hơn thời lượng của ca làm.')
                )

    @api.constrains('grace_minutes')
    def _check_grace_minutes(self):
        for policy in self:
            if policy.grace_minutes < 0:
                raise ValidationError(_('Thời gian ân hạn không được là số âm.'))

    @api.constrains(
        'late_occurrence_threshold', 'late_minutes_threshold',
        'early_leave_occurrence_threshold', 'early_leave_minutes_threshold',
    )
    def _check_alert_thresholds(self):
        for policy in self:
            thresholds = [
                policy.late_occurrence_threshold,
                policy.late_minutes_threshold,
                policy.early_leave_occurrence_threshold,
                policy.early_leave_minutes_threshold,
            ]
            if any(threshold <= 0 for threshold in thresholds):
                raise ValidationError(_('Các ngưỡng cảnh báo phải lớn hơn 0.'))
