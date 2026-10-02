from datetime import timedelta

from odoo import api, fields, models


class ChamCong(models.Model):
    _inherit = 'hr.attendance'

    so_phut_di_muon = fields.Integer(
        string='Số phút đi muộn',
        compute='_tinh_thong_tin_cham_cong',
        store=True
    )

    trang_thai_cham_cong = fields.Selection(
        [
            ('dung_gio', 'Đúng giờ'),
            ('di_muon', 'Đi muộn'),
            ('ve_som', 'Về sớm'),
            ('di_muon_va_ve_som', 'Đi muộn và về sớm'),
            ('thieu_check_out', 'Chưa check-out'),
        ],
        string='Trạng thái',
        compute='_tinh_thong_tin_cham_cong',
        store=True
    )

    so_phut_ve_som = fields.Integer(
        string='Số phút về sớm',
        compute='_tinh_thong_tin_cham_cong',
        store=True,
    )

    thieu_check_out = fields.Boolean(
        string='Chưa check-out',
        compute='_tinh_thong_tin_cham_cong',
        store=True,
    )

    so_phut_lam_thieu = fields.Integer(
        string='Số phút làm thiếu',
        compute='_tinh_thong_tin_cham_cong',
        store=True,
    )

    def _lay_chinh_sach_cham_cong(self, nhan_vien):
        """Lấy chính sách riêng của phòng ban trước, rồi đến chính sách chung."""
        cong_ty = nhan_vien.company_id or self.env.company
        mien_tim_kiem = [
            ('active', '=', True),
            ('company_id', '=', cong_ty.id),
        ]

        if nhan_vien.department_id:
            chinh_sach_phong_ban = self.env['hr.attendance.policy'].sudo().search(
                mien_tim_kiem + [
                    ('department_id', '=', nhan_vien.department_id.id),
                ],
                limit=1,
            )
            if chinh_sach_phong_ban:
                return chinh_sach_phong_ban

        return self.env['hr.attendance.policy'].sudo().search(
            mien_tim_kiem + [('department_id', '=', False)],
            limit=1,
        )

    def _lay_thong_tin_ca_lam(self, nhan_vien, gio_cham_cong):
        """Trả về mốc thời gian và quy tắc tính cho ca làm của nhân viên."""
        chinh_sach = self._lay_chinh_sach_cham_cong(nhan_vien)

        # Giữ nguyên quy tắc cũ nếu hệ thống chưa có chính sách nào.
        gio_bat_dau = gio_cham_cong.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0,
        )
        gio_ket_thuc = gio_cham_cong.replace(
            hour=17,
            minute=0,
            second=0,
            microsecond=0,
        )
        thoi_gian_an_han = 0
        so_phut_lam_toi_thieu = 8 * 60

        if chinh_sach:
            tong_phut_bat_dau = round(chinh_sach.start_hour * 60)
            tong_phut_ket_thuc = round(chinh_sach.end_hour * 60)
            gio_bat_dau = gio_cham_cong.replace(
                hour=tong_phut_bat_dau // 60,
                minute=tong_phut_bat_dau % 60,
                second=0,
                microsecond=0,
            )
            gio_ket_thuc = gio_cham_cong.replace(
                hour=tong_phut_ket_thuc // 60,
                minute=tong_phut_ket_thuc % 60,
                second=0,
                microsecond=0,
            )
            thoi_gian_an_han = chinh_sach.grace_minutes
            so_phut_lam_toi_thieu = round(chinh_sach.required_work_hours * 60)

        return (
            gio_bat_dau,
            gio_ket_thuc,
            thoi_gian_an_han,
            so_phut_lam_toi_thieu,
        )

    def name_get(self):
        ket_qua = []

        for ban_ghi in self:
            if ban_ghi.check_in:
                gio_cham_cong = fields.Datetime.context_timestamp(
                    ban_ghi,
                    ban_ghi.check_in
                )

                ngay = gio_cham_cong.strftime('%d/%m/%Y')
                gio = gio_cham_cong.strftime('%H:%M')

                ket_qua.append((
                    ban_ghi.id,
                    f'{ngay} - {gio} - {ban_ghi.so_phut_di_muon} phút'
                ))
            else:
                ket_qua.append((
                    ban_ghi.id,
                    'Chưa có thời gian chấm công'
                ))

        return ket_qua
    @api.depends('check_in', 'check_out', 'employee_id')
    def _tinh_thong_tin_cham_cong(self):
        for ban_ghi in self:
            ban_ghi.so_phut_di_muon = 0
            ban_ghi.so_phut_ve_som = 0
            ban_ghi.so_phut_lam_thieu = 0
            ban_ghi.thieu_check_out = False
            ban_ghi.trang_thai_cham_cong = 'dung_gio'

            if not ban_ghi.check_in:
                continue

            gio_cham_cong = fields.Datetime.context_timestamp(
                ban_ghi,
                ban_ghi.check_in
            )

            (
                gio_bat_dau,
                gio_ket_thuc,
                thoi_gian_an_han,
                so_phut_lam_toi_thieu,
            ) = ban_ghi._lay_thong_tin_ca_lam(
                    ban_ghi.employee_id,
                    gio_cham_cong,
            )
            gio_bat_dau_co_an_han = gio_bat_dau + timedelta(
                minutes=thoi_gian_an_han,
            )

            di_muon = False
            ve_som = False

          
            if gio_cham_cong > gio_bat_dau_co_an_han:
                so_giay_di_muon = (
                    gio_cham_cong - gio_bat_dau_co_an_han
                ).total_seconds()

                ban_ghi.so_phut_di_muon = int(
                    so_giay_di_muon / 60
                )

                ban_ghi.trang_thai_cham_cong = 'di_muon'
                di_muon = True

                ban_ghi.so_phut_di_muon = int(
                    so_giay_di_muon / 60
                )

                ban_ghi.trang_thai_cham_cong = 'di_muon'
                di_muon = True

            if not ban_ghi.check_out:
                ban_ghi.thieu_check_out = True
                ban_ghi.trang_thai_cham_cong = 'thieu_check_out'
                continue

            gio_check_out = fields.Datetime.context_timestamp(
                ban_ghi,
                ban_ghi.check_out,
            )

            if gio_check_out < gio_ket_thuc:
                so_giay_ve_som = (gio_ket_thuc - gio_check_out).total_seconds()
                ban_ghi.so_phut_ve_som = int(so_giay_ve_som / 60)
                ve_som = True

            so_phut_lam_thuc_te = int(
                (gio_check_out - gio_cham_cong).total_seconds() / 60
            )
            ban_ghi.so_phut_lam_thieu = max(
                so_phut_lam_toi_thieu - so_phut_lam_thuc_te,
                0,
            )

            if di_muon and ve_som:
                ban_ghi.trang_thai_cham_cong = 'di_muon_va_ve_som'
            elif ve_som:
                ban_ghi.trang_thai_cham_cong = 've_som'
