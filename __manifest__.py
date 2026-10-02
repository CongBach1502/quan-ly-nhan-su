{
    'name': 'HR Data Analysis',
    'version': '16.0.1.10.0',
    'category': 'Human Resources',
    'summary': 'Quản lý nhân sự và phân tích dữ liệu',
    'depends': [
        'hr',
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
    'security/phan_quyen.xml',
    'security/quy_tac_ban_ghi.xml',
    'security/ir.model.access.csv',

    'views/nhan_vien_views.xml',
    'views/chinh_sach_cham_cong_views.xml',
    'views/canh_bao_cham_cong_views.xml',
    'views/phan_tich_cham_cong_views.xml',
    'views/phan_nhom_cham_cong_views.xml',
    'views/ai_insight_cham_cong_views.xml',
    'views/cham_cong_views.xml',
    'views/giai_trinh_di_muon_views.xml',
],
    'installable': True,
    'application': True,
}
