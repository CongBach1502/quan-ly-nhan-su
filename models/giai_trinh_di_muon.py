from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GiaiTrinhDiMuon(models.Model):
    _name = 'hr.giai.trinh.di.muon'
    _description = 'Giải trình chấm công'
    _order = 'ngay_giai_trinh desc'

    nhan_vien_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        required=True
    )

    cham_cong_id = fields.Many2one(
        'hr.attendance',
        string='Bản chấm công',
        required=True,
        domain="['&', ('employee_id', '=', nhan_vien_id), '|', ('so_phut_di_muon', '>', 0), ('so_phut_ve_som', '>', 0)]"
    )

    ngay_giai_trinh = fields.Date(
        string='Ngày',
        required=True
    )

    so_phut_di_muon = fields.Integer(
        string='Số phút đi muộn',
        related='cham_cong_id.so_phut_di_muon',
        store=True,
        readonly=True
    )

    so_phut_ve_som = fields.Integer(
        string='Số phút về sớm',
        related='cham_cong_id.so_phut_ve_som',
        store=True,
        readonly=True,
    )

    loai_vi_pham = fields.Selection(
        [
            ('di_muon', 'Đi muộn'),
            ('ve_som', 'Về sớm'),
            ('di_muon_va_ve_som', 'Đi muộn và về sớm'),
        ],
        string='Loại vi phạm',
        compute='_tinh_loai_vi_pham',
        store=True,
        readonly=True,
    )

    ly_do = fields.Text(
        string='Lý do giải trình',
        required=True
    )

    trang_thai = fields.Selection(
        [
            ('cho_xac_nhan', 'Chờ xác nhận'),
            ('da_xac_nhan', 'Đã xác nhận'),
            ('tu_choi', 'Từ chối'),
        ],
        string='Trạng thái',
        default='cho_xac_nhan',
        required=True
    )

    ly_do_tu_choi = fields.Text(
        string='Lý do từ chối'
    )

    minh_chung_ids = fields.Many2many(
        'ir.attachment',
        'hr_giai_trinh_di_muon_attachment_rel',
        'giai_trinh_id',
        'attachment_id',
        string='Minh chứng đính kèm',
    )

    nguoi_duyet_id = fields.Many2one(
        'res.users',
        string='Người xử lý',
        readonly=True,
    )

    ngay_duyet = fields.Datetime(
        string='Ngày xử lý',
        readonly=True,
    )

    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    @api.depends('cham_cong_id.so_phut_di_muon', 'cham_cong_id.so_phut_ve_som')
    def _tinh_loai_vi_pham(self):
        for ban_ghi in self:
            if ban_ghi.so_phut_di_muon > 0 and ban_ghi.so_phut_ve_som > 0:
                ban_ghi.loai_vi_pham = 'di_muon_va_ve_som'
            elif ban_ghi.so_phut_di_muon > 0:
                ban_ghi.loai_vi_pham = 'di_muon'
            elif ban_ghi.so_phut_ve_som > 0:
                ban_ghi.loai_vi_pham = 've_som'
            else:
                ban_ghi.loai_vi_pham = False

    @api.constrains('cham_cong_id', 'trang_thai')
    def _check_giai_trinh_trung(self):
        for ban_ghi in self:
            if not ban_ghi.cham_cong_id or ban_ghi.trang_thai == 'tu_choi':
                continue

            giai_trinh_trung = self.search_count([
                ('id', '!=', ban_ghi.id),
                ('cham_cong_id', '=', ban_ghi.cham_cong_id.id),
                ('trang_thai', 'in', ['cho_xac_nhan', 'da_xac_nhan']),
            ])
            if giai_trinh_trung:
                raise ValidationError(
                    _('Bản chấm công này đã có giải trình đang chờ xác nhận hoặc đã được xác nhận.')
                )
    @api.model
    def default_get(self, fields_list):
        gia_tri_mac_dinh = super().default_get(fields_list)

        if self.env.user.employee_id:
            gia_tri_mac_dinh['nhan_vien_id'] = self.env.user.employee_id.id

        return gia_tri_mac_dinh

    @api.onchange('cham_cong_id')
    def _onchange_cham_cong_id(self):
        if not self.cham_cong_id:
            return

        self.nhan_vien_id = self.cham_cong_id.employee_id

        if self.cham_cong_id.check_in:
            gio_cham_cong = fields.Datetime.context_timestamp(
                self,
                self.cham_cong_id.check_in
            )

            self.ngay_giai_trinh = gio_cham_cong.date()

    @api.onchange('nhan_vien_id')
    def _onchange_nhan_vien_id(self):
        if not self.env.user.has_group(
            'hr_data_analysis.group_hr_data_analysis_manager'
        ):
            if self.env.user.employee_id:
                self.nhan_vien_id = self.env.user.employee_id

        self.cham_cong_id = False
        self.ngay_giai_trinh = False

    @api.onchange('nhan_vien_id')
    def _loc_ban_cham_cong(self):
        if not self.nhan_vien_id:
            return {
                'domain': {
                    'cham_cong_id': []
                }
            }

        cac_ban_cham_cong_da_xu_ly = self.env[
            'hr.giai.trinh.di.muon'
        ].search([
            ('nhan_vien_id', '=', self.nhan_vien_id.id),
            ('trang_thai', 'in', [
                'cho_xac_nhan',
                'da_xac_nhan'
            ]),
        ])

        cac_ban_cham_cong_da_xu_ly_ids = (
            cac_ban_cham_cong_da_xu_ly.mapped('cham_cong_id').ids
        )

        return {
            'domain': {
                'cham_cong_id': [
                    '&',
                    ('employee_id', '=', self.nhan_vien_id.id),
                    '&',
                    '|',
                    ('so_phut_di_muon', '>', 0),
                    ('so_phut_ve_som', '>', 0),
                    ('id', 'not in', cac_ban_cham_cong_da_xu_ly_ids),
                ]
            }
        }
    

    def action_xac_nhan(self):
        if not self.env.user.has_group(
            'hr_data_analysis.group_hr_data_analysis_manager'
        ):
            return False

        for ban_ghi in self:
            if ban_ghi.trang_thai != 'cho_xac_nhan':
                continue
            ban_ghi.write({
                'trang_thai': 'da_xac_nhan',
                'nguoi_duyet_id': self.env.user.id,
                'ngay_duyet': fields.Datetime.now(),
            })


    def action_tu_choi(self):
        if not self.env.user.has_group(
            'hr_data_analysis.group_hr_data_analysis_manager'
        ):
            return False

        for ban_ghi in self:
            if ban_ghi.trang_thai != 'cho_xac_nhan':
                continue
            if not ban_ghi.ly_do_tu_choi or not ban_ghi.ly_do_tu_choi.strip():
                raise ValidationError(_('Vui lòng nhập lý do từ chối trước khi xử lý.'))
            ban_ghi.write({
                'trang_thai': 'tu_choi',
                'nguoi_duyet_id': self.env.user.id,
                'ngay_duyet': fields.Datetime.now(),
            })
