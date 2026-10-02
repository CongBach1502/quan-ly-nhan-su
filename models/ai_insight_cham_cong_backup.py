from datetime import date

from odoo import api, fields, models


class HrAttendanceAiInsight(models.Model):
    _name = 'hr.attendance.ai.insight'
    _description = 'AI Insight chấm công'
    _order = 'period_start desc, priority desc, department_id, insight_type'

    insight_type = fields.Selection([
        ('overview', 'Tổng quan'),
        ('department', 'Theo phòng ban'),
        ('cluster', 'Phân nhóm hành vi'),
    ], string='Loại insight', required=True, readonly=True)
    period_start = fields.Date(string='Từ ngày', required=True, readonly=True)
    period_end = fields.Date(string='Đến ngày', required=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban', readonly=True)
    title = fields.Char(string='Tiêu đề', required=True, readonly=True)
    analysis = fields.Text(string='Nhận xét AI', required=True, readonly=True)
    recommendation = fields.Text(string='Gợi ý xử lý', required=True, readonly=True)
    priority = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
    ], string='Mức ưu tiên', required=True, readonly=True)
    generated_at = fields.Datetime(string='Thời điểm tạo', default=fields.Datetime.now, readonly=True)

    @api.model
    def _upsert_insight(self, values):
        domain = [
            ('insight_type', '=', values['insight_type']),
            ('period_start', '=', values['period_start']),
            ('period_end', '=', values['period_end']),
            ('department_id', '=', values.get('department_id', False)),
        ]
        insight = self.search(domain, limit=1)
        if insight:
            insight.write(values)
        else:
            self.create(values)

    @api.model
    def action_generate_current_month_insights(self):
        # Lấy kỳ dữ liệu K-Means mới nhất thay vì cố định tháng hiện tại
        latest_cluster = self.env['hr.attendance.cluster'].search(
            [],
            order='period_end desc, period_start desc',
            limit=1,
        )

        if latest_cluster:
            period_start = latest_cluster.period_start
            period_end = latest_cluster.period_end
        else:
            latest_alert = self.env['hr.attendance.alert'].search(
                [],
                order='period_end desc, period_start desc',
                limit=1,
            )

            if not latest_alert:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'AI Insights',
                    'res_model': self._name,
                    'view_mode': 'tree,form',
                }

            period_start = latest_alert.period_start
            period_end = latest_alert.period_end

        alerts = self.env['hr.attendance.alert'].search([
            ('period_start', '=', period_start),
            ('period_end', '=', period_end),
        ])

        clusters = self.env['hr.attendance.cluster'].search([
            ('period_start', '=', period_start),
            ('period_end', '=', period_end),
        ])

        # =========================
        # 1. TỔNG QUAN RỦI RO
        # =========================
        high_risk_alerts = alerts.filtered(
            lambda alert: alert.risk_level == 'high'
        )

        total_minutes = sum(
            alert.total_violation_minutes
            for alert in alerts
        )

        top_alert = max(
            alerts,
            key=lambda alert: alert.risk_score,
            default=False
        )

        if top_alert:
            overview_analysis = (
                f'Kỳ {period_start} đến {period_end} có '
                f'{len(alerts)} cảnh báo chấm công, trong đó '
                f'{len(high_risk_alerts)} cảnh báo rủi ro cao. '
                f'Tổng thời gian vi phạm là {total_minutes} phút. '
                f'Nhân viên cần ưu tiên theo dõi là '
                f'{top_alert.employee_id.name} với điểm rủi ro '
                f'{top_alert.risk_score}/100.'
            )

            overview_recommendation = (
                'Ưu tiên trao đổi với các nhân viên rủi ro cao, '
                'kiểm tra nguyên nhân thực tế và theo dõi lại '
                'trong kỳ tiếp theo.'
            )

            priority = 'high' if high_risk_alerts else 'medium'

        else:
            overview_analysis = (
                f'Kỳ {period_start} đến {period_end} '
                'chưa có cảnh báo chấm công vượt ngưỡng đã cấu hình.'
            )

            overview_recommendation = (
                'Tiếp tục theo dõi dữ liệu chấm công và giữ '
                'ngưỡng cảnh báo phù hợp với chính sách công ty.'
            )

            priority = 'low'

        self._upsert_insight({
            'insight_type': 'overview',
            'period_start': period_start,
            'period_end': period_end,
            'title': 'Tổng quan rủi ro chấm công',
            'analysis': overview_analysis,
            'recommendation': overview_recommendation,
            'priority': priority,
        })

        # =========================
        # 2. PHÂN TÍCH THEO PHÒNG BAN
        # =========================
        departments = alerts.mapped('department_id')

        for department in departments:
            department_alerts = alerts.filtered(
                lambda alert: alert.department_id == department
            )

            department_high_risk = department_alerts.filtered(
                lambda alert: alert.risk_level == 'high'
            )

            department_minutes = sum(
                alert.total_violation_minutes
                for alert in department_alerts
            )

            department_priority = (
                'high' if department_high_risk else 'medium'
            )

            self._upsert_insight({
                'insight_type': 'department',
                'period_start': period_start,
                'period_end': period_end,
                'department_id': department.id,
                'title': f'Rủi ro chấm công - {department.name}',
                'analysis': (
                    f'Phòng ban có {len(department_alerts)} cảnh báo, '
                    f'{len(department_high_risk)} trường hợp rủi ro cao '
                    f'và tổng {department_minutes} phút vi phạm '
                    f'trong kỳ.'
                ),
                'recommendation': (
                    'Trưởng phòng nên rà soát lịch làm việc, '
                    'trao đổi với nhân viên liên quan và theo dõi '
                    'xu hướng ở kỳ sau.'
                ),
                'priority': department_priority,
            })

        # =========================
        # 3. NHẬN XÉT K-MEANS
        # =========================
        cluster_counts = {}

        for cluster in clusters:
            cluster_counts[cluster.cluster_name] = (
                cluster_counts.get(cluster.cluster_name, 0) + 1
            )

        if cluster_counts:
            summary = ', '.join(
                f'{name}: {count} nhân viên'
                for name, count in sorted(cluster_counts.items())
            )

            highest_cluster = max(
                cluster_counts,
                key=cluster_counts.get
            )

            cluster_analysis = (
                f'Kết quả K-Means trong kỳ {period_start} đến '
                f'{period_end}: {summary}. '
                f'Nhóm có quy mô lớn nhất là '
                f'“{highest_cluster}”.'
            )

            cluster_recommendation = (
                'Dùng kết quả này để chọn nhóm cần theo dõi '
                'và so sánh thay đổi giữa các kỳ.'
            )

        else:
            cluster_analysis = (
                f'Chưa có kết quả phân nhóm K-Means cho kỳ '
                f'{period_start} đến {period_end}.'
            )

            cluster_recommendation = (
                'Chạy chức năng “Phân nhóm K-Means tháng này” '
                'trước khi tạo lại AI Insight.'
            )

        self._upsert_insight({
            'insight_type': 'cluster',
            'period_start': period_start,
            'period_end': period_end,
            'title': 'Nhận xét từ phân nhóm K-Means',
            'analysis': cluster_analysis,
            'recommendation': cluster_recommendation,
            'priority': 'medium' if cluster_counts else 'low',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'AI Insights',
            'res_model': self._name,
            'view_mode': 'tree,form',
            'domain': [
                ('period_start', '=', period_start),
                ('period_end', '=', period_end),
            ],
        }