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
        """Tạo insight theo kỳ K-Means mới nhất, bổ sung số liệu hành vi thực tế."""
        latest_cluster = self.env['hr.attendance.cluster'].search(
            [], order='period_end desc, period_start desc', limit=1
        )
        if latest_cluster:
            period_start, period_end = latest_cluster.period_start, latest_cluster.period_end
        else:
            latest_alert = self.env['hr.attendance.alert'].search(
                [], order='period_end desc, period_start desc', limit=1
            )
            if not latest_alert:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'AI Insights',
                    'res_model': self._name,
                    'view_mode': 'tree,form',
                }
            period_start, period_end = latest_alert.period_start, latest_alert.period_end

        alerts = self.env['hr.attendance.alert'].search([
            ('period_start', '=', period_start), ('period_end', '=', period_end),
        ])
        clusters = self.env['hr.attendance.cluster'].search([
            ('period_start', '=', period_start), ('period_end', '=', period_end),
        ])

        # Tổng hợp số liệu K-Means theo nhóm và phòng ban.
        by_cluster = {}
        by_department = {}
        for record in clusters:
            name = record.cluster_name or 'Chưa phân nhóm'
            stat = by_cluster.setdefault(name, {
                'employees': 0, 'late_count': 0, 'late_minutes': 0,
                'early_count': 0, 'early_minutes': 0,
            })
            stat['employees'] += 1
            stat['late_count'] += record.late_count or 0
            stat['late_minutes'] += record.late_minutes or 0
            stat['early_count'] += record.early_leave_count or 0
            stat['early_minutes'] += record.early_leave_minutes or 0

            dep_id = record.department_id.id or False
            dep = by_department.setdefault(dep_id, {
                'employees': 0, 'late_count': 0, 'late_minutes': 0,
                'early_count': 0, 'early_minutes': 0,
            })
            dep['employees'] += 1
            dep['late_count'] += record.late_count or 0
            dep['late_minutes'] += record.late_minutes or 0
            dep['early_count'] += record.early_leave_count or 0
            dep['early_minutes'] += record.early_leave_minutes or 0

        total_late_count = sum(s['late_count'] for s in by_cluster.values())
        total_late_minutes = sum(s['late_minutes'] for s in by_cluster.values())
        total_early_count = sum(s['early_count'] for s in by_cluster.values())
        total_early_minutes = sum(s['early_minutes'] for s in by_cluster.values())

        high_alerts = alerts.filtered(lambda a: a.risk_level == 'high')
        alert_minutes = sum(a.total_violation_minutes or 0 for a in alerts)
        top_alert = max(alerts, key=lambda a: a.risk_score or 0, default=False)

        if alerts:
            overview = (
                f'Kỳ {period_start} đến {period_end} có {len(alerts)} bản ghi cảnh báo, '
                f'trong đó {len(high_alerts)} cảnh báo rủi ro cao; '
                f'tổng thời gian vi phạm trong các cảnh báo là {alert_minutes} phút. '
            )
            if top_alert:
                overview += (
                    f'Bản ghi có điểm rủi ro cao nhất thuộc về '
                    f'{top_alert.employee_id.name} ({top_alert.risk_score}/100). '
                )
        else:
            overview = (
                f'Kỳ {period_start} đến {period_end} không có bản ghi cảnh báo '
                f'vượt ngưỡng trong mô hình cảnh báo hiện tại. Điều này không đồng nghĩa '
                f'với việc mọi nhân viên đều không có đi muộn hoặc về sớm. '
            )
        if clusters:
            overview += (
                f'Trong {len(clusters)} kết quả K-Means, ghi nhận {total_late_count} lượt đi muộn '
                f'({total_late_minutes} phút) và {total_early_count} lượt về sớm '
                f'({total_early_minutes} phút).'
            )
        self._upsert_insight({
            'insight_type': 'overview',
            'period_start': period_start,
            'period_end': period_end,
            'title': 'Tổng quan rủi ro chấm công',
            'analysis': overview,
            'recommendation': (
                'Đối chiếu các trường hợp có tổng phút đi muộn/về sớm cao với ca làm, '
                'đơn nghỉ và giải trình đã duyệt. Xác minh nguyên nhân trước khi kết luận '
                'và theo dõi thay đổi ở kỳ tiếp theo.'
            ),
            'priority': 'high' if high_alerts else (
                'medium' if total_late_minutes + total_early_minutes else 'low'
            ),
        })

        # Insight theo phòng ban, dựa trên K-Means và cảnh báo cùng kỳ.
        department_ids = set(by_department)
        department_ids.update(a.department_id.id for a in alerts if a.department_id)
        for dep_id in department_ids:
            department = self.env['hr.department'].browse(dep_id) if dep_id else self.env['hr.department']
            dep_name = department.name if department else 'Chưa phân phòng ban'
            stat = by_department.get(dep_id, {})
            dep_alerts = alerts.filtered(lambda a: a.department_id.id == dep_id)
            dep_high = dep_alerts.filtered(lambda a: a.risk_level == 'high')
            alert_dep_minutes = sum(a.total_violation_minutes or 0 for a in dep_alerts)
            dep_late = stat.get('late_minutes', 0)
            dep_early = stat.get('early_minutes', 0)
            analysis = (
                f'Phòng ban {dep_name}: {stat.get("employees", 0)} nhân viên có kết quả K-Means; '
                f'{stat.get("late_count", 0)} lượt đi muộn ({dep_late} phút), '
                f'{stat.get("early_count", 0)} lượt về sớm ({dep_early} phút). '
                f'Có {len(dep_alerts)} bản ghi cảnh báo, trong đó {len(dep_high)} rủi ro cao; '
                f'tổng phút vi phạm ghi nhận trong cảnh báo là {alert_dep_minutes}.'
            )
            self._upsert_insight({
                'insight_type': 'department',
                'period_start': period_start,
                'period_end': period_end,
                'department_id': dep_id or False,
                'title': f'Rủi ro chấm công - {dep_name}',
                'analysis': analysis,
                'recommendation': (
                    'Đối chiếu dữ liệu với lịch làm việc, đơn nghỉ và giải trình đã duyệt. '
                    'Ưu tiên xác minh trường hợp có tổng phút đi muộn/về sớm cao; '
                    'không kết luận vi phạm chỉ dựa trên nhãn phân nhóm.'
                ),
                'priority': 'high' if dep_high else (
                    'medium' if dep_late + dep_early or dep_alerts else 'low'
                ),
            })

        # Insight K-Means chi tiết theo nhóm.
        if by_cluster:
            parts = []
            for name in sorted(by_cluster):
                s = by_cluster[name]
                parts.append(
                    f'{name}: {s["employees"]} nhân viên, {s["late_count"]} lượt đi muộn '
                    f'({s["late_minutes"]} phút), {s["early_count"]} lượt về sớm '
                    f'({s["early_minutes"]} phút)'
                )
            largest = max(by_cluster.items(), key=lambda item: item[1]['employees'])
            most_minutes = max(
                by_cluster.items(),
                key=lambda item: item[1]['late_minutes'] + item[1]['early_minutes'],
            )
            cluster_analysis = (
                f'Kết quả K-Means kỳ {period_start} đến {period_end}: '
                + '; '.join(parts)
                + f'. Nhóm đông nhất là {largest[0]} ({largest[1]["employees"]} nhân viên). '
                + f'Nhóm có tổng phút đi muộn và về sớm cao nhất là {most_minutes[0]} '
                + f'({most_minutes[1]["late_minutes"] + most_minutes[1]["early_minutes"]} phút).'
            )
            cluster_priority = 'high' if (
                most_minutes[1]['late_minutes'] + most_minutes[1]['early_minutes'] > 0
            ) else 'medium'
            cluster_recommendation = (
                'Rà soát số liệu và nguyên nhân thực tế của các nhóm, đối chiếu lịch làm việc '
                'và giải trình đã duyệt; so sánh với kỳ tiếp theo để nhận biết xu hướng.'
            )
        else:
            cluster_analysis = f'Chưa có kết quả K-Means cho kỳ {period_start} đến {period_end}.'
            cluster_priority = 'low'
            cluster_recommendation = 'Chạy chức năng phân nhóm K-Means trước khi tạo AI Insight.'

        self._upsert_insight({
            'insight_type': 'cluster',
            'period_start': period_start,
            'period_end': period_end,
            'title': 'Nhận xét từ phân nhóm K-Means',
            'analysis': cluster_analysis,
            'recommendation': cluster_recommendation,
            'priority': cluster_priority,
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

