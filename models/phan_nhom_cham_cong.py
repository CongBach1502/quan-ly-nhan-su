from collections import defaultdict
from datetime import date, datetime, time
from math import sqrt

from odoo import api, fields, models


class HrAttendanceCluster(models.Model):
    _name = 'hr.attendance.cluster'
    _description = 'Phân nhóm hành vi chấm công'
    _order = 'period_start desc, cluster_number, employee_id'

    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True, readonly=True)
    period_start = fields.Date(string='Từ ngày', required=True, readonly=True)
    period_end = fields.Date(string='Đến ngày', required=True, readonly=True)
    cluster_number = fields.Integer(string='Nhóm K-Means', readonly=True)
    cluster_name = fields.Char(string='Tên nhóm', readonly=True)
    attendance_days = fields.Integer(string='Số ngày chấm công', readonly=True)
    late_count = fields.Integer(string='Số lần đi muộn', readonly=True)
    late_minutes = fields.Integer(string='Tổng phút đi muộn', readonly=True)
    early_leave_count = fields.Integer(string='Số lần về sớm', readonly=True)
    early_leave_minutes = fields.Integer(string='Tổng phút về sớm', readonly=True)
    average_worked_hours = fields.Float(string='Giờ làm trung bình', readonly=True, digits=(16, 2))

    _sql_constraints = [
        ('employee_period_cluster_unique', 'unique(employee_id, period_start, period_end)', 'Nhân viên đã có kết quả phân nhóm cho kỳ này.'),
    ]

    @api.model
    def _run_kmeans(self, feature_rows, cluster_count):
        """K-Means tối giản, không cần thư viện bên ngoài Odoo."""
        column_count = len(feature_rows[0])
        means = [sum(row[index] for row in feature_rows) / len(feature_rows) for index in range(column_count)]
        standard_deviations = []
        for index in range(column_count):
            variance = sum((row[index] - means[index]) ** 2 for row in feature_rows) / len(feature_rows)
            standard_deviations.append(sqrt(variance) or 1)
        normalized = [
            [(value - means[index]) / standard_deviations[index] for index, value in enumerate(row)]
            for row in feature_rows
        ]
        centroids = [normalized[round(index * (len(normalized) - 1) / max(cluster_count - 1, 1))][:] for index in range(cluster_count)]
        assignments = [0] * len(normalized)
        for _iteration in range(30):
            new_assignments = [
                min(range(cluster_count), key=lambda cluster: sum((value - centroids[cluster][index]) ** 2 for index, value in enumerate(row)))
                for row in normalized
            ]
            if new_assignments == assignments and _iteration:
                break
            assignments = new_assignments
            for cluster in range(cluster_count):
                members = [row for index, row in enumerate(normalized) if assignments[index] == cluster]
                if members:
                    centroids[cluster] = [sum(row[index] for row in members) / len(members) for index in range(column_count)]
        return assignments

    @api.model
    def action_generate_current_month_clusters(self):
        """
        Tạo kết quả K-Means dựa trên toàn bộ khoảng thời gian
        đang có dữ liệu chấm công trong Odoo.
        """

        # ============================================================
        # 1. Lấy toàn bộ dữ liệu chấm công hiện có
        # ============================================================
        attendances = self.env['hr.attendance'].search(
            [('check_in', '!=', False)],
            order='check_in asc'
        )

        if not attendances:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Kết quả phân nhóm',
                'res_model': self._name,
                'view_mode': 'tree,form',
            }

        # ============================================================
        # 2. Xác định khoảng thời gian thực tế của bộ dữ liệu
        # ============================================================
        first_check_in = fields.Datetime.context_timestamp(
            attendances[0],
            attendances[0].check_in
        )
        last_check_in = fields.Datetime.context_timestamp(
            attendances[-1],
            attendances[-1].check_in
        )

        period_start = first_check_in.date()
        period_end = last_check_in.date()

        # ============================================================
        # 3. Tổng hợp dữ liệu theo nhân viên
        # ============================================================
        metrics = defaultdict(
            lambda: {
                'days': set(),
                'count': 0,
                'late_count': 0,
                'late_minutes': 0,
                'early_count': 0,
                'early_minutes': 0,
                'worked_hours': 0.0,
            }
        )

        for attendance in attendances:

            if not attendance.employee_id:
                continue

            item = metrics[attendance.employee_id.id]

            # Ngày chấm công
            local_check_in = fields.Datetime.context_timestamp(
                attendance,
                attendance.check_in
            )

            item['days'].add(local_check_in.date())

            # Số lượt chấm công
            item['count'] += 1

            # Đi muộn
            late_minutes = attendance.so_phut_di_muon or 0

            if late_minutes > 0:
                item['late_count'] += 1
                item['late_minutes'] += late_minutes

            # Về sớm
            early_minutes = attendance.so_phut_ve_som or 0

            if early_minutes > 0:
                item['early_count'] += 1
                item['early_minutes'] += early_minutes

            # Giờ làm việc
            item['worked_hours'] += attendance.worked_hours or 0.0

        employee_ids = list(metrics.keys())

        if not employee_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Kết quả phân nhóm',
                'res_model': self._name,
                'view_mode': 'tree,form',
            }

        # ============================================================
        # 4. Tạo các đặc trưng cho K-Means
        # ============================================================
        feature_rows = []

        for employee_id in employee_ids:

            item = metrics[employee_id]

            average_worked_hours = (
                item['worked_hours'] / item['count']
                if item['count']
                else 0.0
            )

            feature_rows.append([
                len(item['days']),
                item['late_count'],
                item['late_minutes'],
                item['early_count'],
                item['early_minutes'],
                average_worked_hours,
            ])

        # ============================================================
        # 5. Chạy K-Means
        # ============================================================
        cluster_count = min(3, len(feature_rows))

        assignments = self._run_kmeans(
            feature_rows,
            cluster_count
        )

        # ============================================================
        # 6. Xác định mức độ của từng nhóm
        # ============================================================
        severity = {
            cluster: 0
            for cluster in set(assignments)
        }

        for index, cluster in enumerate(assignments):

            severity[cluster] += (
                feature_rows[index][2]
                + feature_rows[index][4]
            )

        ordered_clusters = sorted(
            severity,
            key=severity.get
        )

        labels = [
            'Nhóm tuân thủ tốt',
            'Nhóm cần theo dõi',
            'Nhóm rủi ro cao',
        ]

        cluster_labels = {
            cluster: labels[min(rank, 2)]
            for rank, cluster in enumerate(ordered_clusters)
        }

        # ============================================================
        # 7. Tạo / cập nhật kết quả cho từng nhân viên
        # ============================================================
        for index, employee_id in enumerate(employee_ids):

            item = metrics[employee_id]

            average_worked_hours = (
                item['worked_hours'] / item['count']
                if item['count']
                else 0.0
            )

            values = {
                'employee_id': employee_id,
                'period_start': period_start,
                'period_end': period_end,

                'cluster_number': assignments[index],
                'cluster_name': cluster_labels[
                    assignments[index]
                ],

                'attendance_days': len(item['days']),

                'late_count': item['late_count'],
                'late_minutes': item['late_minutes'],

                'early_leave_count': item['early_count'],
                'early_leave_minutes': item['early_minutes'],

                'average_worked_hours':
                    average_worked_hours,
            }

            existing = self.search([
                ('employee_id', '=', employee_id),
                ('period_start', '=', period_start),
                ('period_end', '=', period_end),
            ], limit=1)

            if existing:
                existing.write(values)
            else:
                self.create(values)

        # ============================================================
        # 8. Mở màn hình kết quả
        # ============================================================
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kết quả phân nhóm',
            'res_model': self._name,
            'view_mode': 'tree,form',
            'domain': [
                ('period_start', '=', period_start),
                ('period_end', '=', period_end),
            ],
        }