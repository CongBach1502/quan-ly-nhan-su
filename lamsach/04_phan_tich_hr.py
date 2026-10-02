from pathlib import Path
import pandas as pd
import numpy as np


print("=" * 70)
print("4. PHÂN TÍCH DỮ LIỆU NHÂN SỰ HR")
print("=" * 70)


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

thu_muc = Path(__file__).parent
thu_muc_output = thu_muc / "output"
thu_muc_phan_tich = thu_muc_output / "phan_tich"

thu_muc_phan_tich.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. ĐỌC FILE ĐÃ LÀM SẠCH
# ============================================================

def doc_csv(ten_file):

    duong_dan = thu_muc_output / ten_file

    if not duong_dan.exists():

        raise FileNotFoundError(
            f"Không tìm thấy file: {duong_dan}"
        )

    return pd.read_csv(
        duong_dan,
        encoding="utf-8-sig"
    )


nhan_vien = doc_csv("nhan_vien_sach.csv")
phong_ban = doc_csv("phong_ban_sach.csv")
vi_tri = doc_csv("vi_tri_sach.csv")
hop_dong = doc_csv("hop_dong_sach.csv")
cham_cong = doc_csv("cham_cong_sach.csv")
nghi_phep = doc_csv("nghi_phep_sach.csv")

# ============================================================
# CHUẨN HÓA CỘT PHÒNG BAN THEO CẤU TRÚC ODOO
# ============================================================

if "id" in phong_ban.columns and "department_id" not in phong_ban.columns:
    phong_ban = phong_ban.rename(
        columns={
            "id": "department_id"
        }
    )

if "name" in phong_ban.columns and "department_name" not in phong_ban.columns:
    phong_ban = phong_ban.rename(
        columns={
            "name": "department_name"
        }
    )


# ============================================================
# 3. CHUẨN HÓA KIỂU DỮ LIỆU
# ============================================================

# Nhân viên

if "id" in nhan_vien.columns:
    nhan_vien["id"] = pd.to_numeric(
        nhan_vien["id"],
        errors="coerce"
    )

if "department_id" in nhan_vien.columns:
    nhan_vien["department_id"] = pd.to_numeric(
        nhan_vien["department_id"],
        errors="coerce"
    )

if "job_id" in nhan_vien.columns:
    nhan_vien["job_id"] = pd.to_numeric(
        nhan_vien["job_id"],
        errors="coerce"
    )


# Phòng ban

if "department_id" in phong_ban.columns:
    phong_ban["department_id"] = pd.to_numeric(
        phong_ban["department_id"],
        errors="coerce"
    )


# Vị trí

for cot in [
    "job_id",
    "department_id"
]:

    if cot in vi_tri.columns:

        vi_tri[cot] = pd.to_numeric(
            vi_tri[cot],
            errors="coerce"
        )


# Hợp đồng

for cot in [
    "contract_id",
    "employee_id",
    "contract_type_id",
    "wage"
]:

    if cot in hop_dong.columns:

        hop_dong[cot] = pd.to_numeric(
            hop_dong[cot],
            errors="coerce"
        )


# Chấm công

for cot in [
    "id",
    "employee_id",
    "worked_hours",
    "so_phut_di_muon"
]:

    if cot in cham_cong.columns:

        cham_cong[cot] = pd.to_numeric(
            cham_cong[cot],
            errors="coerce"
        )


# Nghỉ phép

for cot in [
    "leave_id",
    "employee_id",
    "holiday_status_id",
    "number_of_days"
]:

    if cot in nghi_phep.columns:

        nghi_phep[cot] = pd.to_numeric(
            nghi_phep[cot],
            errors="coerce"
        )


# Ngày chấm công

if "check_in" in cham_cong.columns:

    cham_cong["check_in"] = pd.to_datetime(
        cham_cong["check_in"],
        errors="coerce"
    )

if "check_out" in cham_cong.columns:

    cham_cong["check_out"] = pd.to_datetime(
        cham_cong["check_out"],
        errors="coerce"
    )


# ============================================================
# 4. PHÂN TÍCH NHÂN VIÊN
# ============================================================

print("\n" + "=" * 70)
print("1. PHÂN TÍCH NHÂN VIÊN")
print("=" * 70)


tong_nhan_vien = len(nhan_vien)

print(
    "Tổng nhân viên:",
    tong_nhan_vien
)


# Active / inactive

if "active" in nhan_vien.columns:

    active_text = (
        nhan_vien["active"]
        .astype(str)
        .str.lower()
    )

    so_active = (
        active_text == "true"
    ).sum()

    so_inactive = (
        active_text == "false"
    ).sum()

    print(
        "Active:",
        so_active
    )

    print(
        "Inactive:",
        so_inactive
    )

else:

    so_active = np.nan
    so_inactive = np.nan


# Giới tính

if "gender" in nhan_vien.columns:

    gender = (
        nhan_vien["gender"]
        .fillna("Chưa xác định")
        .replace("", "Chưa xác định")
    )

    thong_ke_gender = (
        gender
        .value_counts()
        .rename_axis("gender")
        .reset_index(name="so_luong")
    )

    print("\nPhân bố giới tính:")

    print(
        thong_ke_gender.to_string(
            index=False
        )
    )

else:

    thong_ke_gender = pd.DataFrame()


# Loại nhân viên

if "employee_type" in nhan_vien.columns:

    thong_ke_loai_nv = (
        nhan_vien["employee_type"]
        .fillna("Chưa xác định")
        .value_counts()
        .rename_axis("employee_type")
        .reset_index(name="so_luong")
    )

    print("\nLoại nhân viên:")

    print(
        thong_ke_loai_nv.to_string(
            index=False
        )
    )

else:

    thong_ke_loai_nv = pd.DataFrame()


# ============================================================
# 5. PHÂN TÍCH PHÒNG BAN
# ============================================================

print("\n" + "=" * 70)
print("2. PHÂN TÍCH PHÒNG BAN")
print("=" * 70)


if (
    "department_id" in nhan_vien.columns
    and "department_id" in phong_ban.columns
):

    nv_pb = nhan_vien.merge(
        phong_ban[
            [
                "department_id",
                "department_name"
            ]
        ],
        on="department_id",
        how="left"
    )

    nv_pb["department_name"] = (
        nv_pb["department_name"]
        .fillna("Chưa xác định")
    )

    thong_ke_phong_ban = (
        nv_pb
        .groupby(
            [
                "department_id",
                "department_name"
            ],
            dropna=False
        )
        .size()
        .reset_index(name="so_nhan_vien")
        .sort_values(
            "so_nhan_vien",
            ascending=False
        )
    )

    thong_ke_phong_ban["ty_le"] = (
        thong_ke_phong_ban["so_nhan_vien"]
        / tong_nhan_vien
        * 100
    )

    thong_ke_phong_ban["ty_le"] = (
        thong_ke_phong_ban["ty_le"]
        .round(2)
    )

    print(
        thong_ke_phong_ban.to_string(
            index=False
        )
    )

else:

    nv_pb = nhan_vien.copy()

    nv_pb["department_name"] = "Chưa xác định"

    thong_ke_phong_ban = pd.DataFrame()


# ============================================================
# 6. PHÂN TÍCH VỊ TRÍ
# ============================================================

print("\n" + "=" * 70)
print("3. PHÂN TÍCH VỊ TRÍ")
print("=" * 70)


if "job_id" in nhan_vien.columns:

    nv_job = nhan_vien.merge(
        vi_tri[
            [
                "id",
                "name",
                "department_id"
            ]
        ].rename(
            columns={
                "id": "job_id",
                "name": "job_position",
                "department_id": "job_department_id"
            }
        ),
        on="job_id",
        how="left"
    )

    nv_job["job_position"] = (
        nv_job["job_position"]
        .fillna("Chưa xác định")
    )

    thong_ke_vi_tri = (
        nv_job
        .groupby(
            "job_position"
        )
        .size()
        .reset_index(
            name="so_nhan_vien"
        )
        .sort_values(
            "so_nhan_vien",
            ascending=False
        )
    )

    print(
        "Tổng số vị trí trong danh mục:",
        len(vi_tri)
    )

    print(
        "Số vị trí có nhân viên:",
        len(thong_ke_vi_tri)
    )

    print("\nCác vị trí có nhiều nhân viên nhất:")

    print(
        thong_ke_vi_tri
        .head(20)
        .to_string(index=False)
    )

else:

    nv_job = nhan_vien.copy()
    nv_job["job_position"] = "Chưa xác định"
    thong_ke_vi_tri = pd.DataFrame()


# ============================================================
# 7. PHÂN TÍCH HỢP ĐỒNG
# ============================================================

print("\n" + "=" * 70)
print("4. PHÂN TÍCH HỢP ĐỒNG")
print("=" * 70)


tong_hop_dong = len(hop_dong)

print(
    "Tổng hợp đồng:",
    tong_hop_dong
)


if "employee_id" in hop_dong.columns:

    hop_dong_moi_nv = (
        hop_dong
        .groupby("employee_id")
        .size()
        .reset_index(
            name="so_hop_dong"
        )
    )

    print(
        "Nhân viên có hợp đồng:",
        len(hop_dong_moi_nv)
    )

    print(
        "Nhân viên có > 1 hợp đồng:",
        (
            hop_dong_moi_nv["so_hop_dong"] > 1
        ).sum()
    )

    hop_dong_moi_nv = hop_dong_moi_nv.merge(
        nhan_vien[
            [
                "id",
                "name"
            ]
        ],
        left_on="employee_id",
        right_on="id",
        how="left"
    )

    hop_dong_moi_nv = hop_dong_moi_nv[
        [
            "employee_id",
            "name",
            "so_hop_dong"
        ]
    ]


else:

    hop_dong_moi_nv = pd.DataFrame()


# Wage

if "wage" in hop_dong.columns:

    tong_wage = hop_dong["wage"].sum()

    wage_trung_binh = hop_dong["wage"].mean()

    print(
        "Tổng wage:",
        tong_wage
    )

    print(
        "Wage trung bình:",
        wage_trung_binh
    )

    print(
        "Số hợp đồng wage > 0:",
        (
            hop_dong["wage"] > 0
        ).sum()
    )


# Date end

if "date_end" in hop_dong.columns:

    print(
        "Hợp đồng không có date_end:",
        hop_dong["date_end"].isna().sum()
    )


# State

if "state" in hop_dong.columns:

    thong_ke_state_hd = (
        hop_dong["state"]
        .fillna("Chưa xác định")
        .value_counts()
        .rename_axis("state")
        .reset_index(name="so_hop_dong")
    )

    print("\nTrạng thái hợp đồng:")

    print(
        thong_ke_state_hd.to_string(
            index=False
        )
    )

else:

    thong_ke_state_hd = pd.DataFrame()


# ============================================================
# 8. PHÂN TÍCH NGHỈ PHÉP
# ============================================================

print("\n" + "=" * 70)
print("5. PHÂN TÍCH NGHỈ PHÉP")
print("=" * 70)


tong_don_nghi = len(nghi_phep)


if "number_of_days" in nghi_phep.columns:

    tong_ngay_nghi = (
        nghi_phep["number_of_days"]
        .sum()
    )

else:

    tong_ngay_nghi = 0


print(
    "Tổng đơn nghỉ:",
    tong_don_nghi
)

print(
    "Tổng ngày nghỉ:",
    tong_ngay_nghi
)


if (
    "employee_id" in nghi_phep.columns
    and len(nghi_phep) > 0
):

    nghi_phep_nv = (
        nghi_phep
        .groupby("employee_id")[
            "number_of_days"
        ]
        .sum()
        .reset_index()
        .rename(
            columns={
                "number_of_days":
                "tong_ngay_nghi"
            }
        )
    )

    nghi_phep_nv = nghi_phep_nv.merge(
        nhan_vien[
            [
                "id",
                "name"
            ]
        ],
        left_on="employee_id",
        right_on="id",
        how="left"
    )

    nghi_phep_nv = nghi_phep_nv[
        [
            "employee_id",
            "name",
            "tong_ngay_nghi"
        ]
    ]

else:

    nghi_phep_nv = pd.DataFrame()


# ============================================================
# 9. CHUẨN BỊ DỮ LIỆU CHẤM CÔNG
# ============================================================

print("\n" + "=" * 70)
print("6. PHÂN TÍCH CHẤM CÔNG")
print("=" * 70)


if len(cham_cong) > 0:

    # --------------------------------------------------------
    # Tạo ngày
    # --------------------------------------------------------

    cham_cong["ngay"] = (
        cham_cong["check_in"]
        .dt.date
    )

    # --------------------------------------------------------
    # Đổi ngày thành datetime để group dễ hơn
    # --------------------------------------------------------

    cham_cong["ngay"] = pd.to_datetime(
        cham_cong["ngay"]
    )


    # --------------------------------------------------------
    # Tổng quan
    # --------------------------------------------------------

    tong_luot_cc = len(cham_cong)

    tong_gio = (
        cham_cong["worked_hours"]
        .sum()
    )

    gio_tb_luot = (
        cham_cong["worked_hours"]
        .mean()
    )

    tong_phut_muon = (
        cham_cong["so_phut_di_muon"]
        .sum()
    )

    so_luot_muon = (
        cham_cong["so_phut_di_muon"] > 0
    ).sum()

    ty_le_luot_muon = (
        so_luot_muon
        / tong_luot_cc
        * 100
    )

    print(
        "Tổng lượt chấm công:",
        tong_luot_cc
    )

    print(
        "Tổng giờ làm:",
        round(tong_gio, 2)
    )

    print(
        "Giờ làm trung bình / lượt:",
        round(gio_tb_luot, 2)
    )

    print(
        "Tổng phút đi muộn:",
        round(tong_phut_muon, 2)
    )

    print(
        "Số lượt đi muộn:",
        so_luot_muon
    )

    print(
        "Tỷ lệ lượt đi muộn:",
        round(ty_le_luot_muon, 2),
        "%"
    )


    # ========================================================
    # 10. CHẤM CÔNG THEO NGÀY
    # ========================================================

    cham_cong_ngay = (
        cham_cong
        .groupby("ngay")
        .agg(
            so_luot_cham_cong=(
                "employee_id",
                "count"
            ),
            so_nhan_vien=(
                "employee_id",
                "nunique"
            ),
            tong_gio_lam=(
                "worked_hours",
                "sum"
            ),
            gio_tb_moi_luot=(
                "worked_hours",
                "mean"
            ),
            tong_phut_di_muon=(
                "so_phut_di_muon",
                "sum"
            ),
            so_luot_di_muon=(
                "so_phut_di_muon",
                lambda x: (x > 0).sum()
            )
        )
        .reset_index()
    )


    cham_cong_ngay["ty_le_di_muon"] = (
        cham_cong_ngay["so_luot_di_muon"]
        / cham_cong_ngay["so_luot_cham_cong"]
        * 100
    ).round(2)


    print("\nSố ngày có dữ liệu chấm công:")

    print(
        len(cham_cong_ngay)
    )


    # ========================================================
    # 11. CHẤM CÔNG THEO NHÂN VIÊN
    # ========================================================

    cham_cong_nv = (
        cham_cong
        .groupby("employee_id")
        .agg(
            so_luot_cham_cong=(
                "id",
                "count"
            ),
            tong_gio_lam=(
                "worked_hours",
                "sum"
            ),
            gio_tb_moi_luot=(
                "worked_hours",
                "mean"
            ),
            tong_phut_di_muon=(
                "so_phut_di_muon",
                "sum"
            ),
            so_luot_di_muon=(
                "so_phut_di_muon",
                lambda x: (x > 0).sum()
            ),
            so_ngay_cham_cong=(
                "ngay",
                "nunique"
            )
        )
        .reset_index()
    )


    cham_cong_nv["ty_le_di_muon"] = (
        cham_cong_nv["so_luot_di_muon"]
        / cham_cong_nv["so_luot_cham_cong"]
        * 100
    ).round(2)


    cham_cong_nv = cham_cong_nv.merge(
        nhan_vien[
            [
                "id",
                "name",
                "department_id"
            ]
        ],
        left_on="employee_id",
        right_on="id",
        how="left"
    )


    cham_cong_nv = cham_cong_nv.merge(
        phong_ban[
            [
                "department_id",
                "department_name"
            ]
        ],
        on="department_id",
        how="left"
    )


    cham_cong_nv["department_name"] = (
        cham_cong_nv["department_name"]
        .fillna("Chưa xác định")
    )


    cham_cong_nv = cham_cong_nv[
        [
            "employee_id",
            "name",
            "department_id",
            "department_name",
            "so_ngay_cham_cong",
            "so_luot_cham_cong",
            "tong_gio_lam",
            "gio_tb_moi_luot",
            "tong_phut_di_muon",
            "so_luot_di_muon",
            "ty_le_di_muon"
        ]
    ]


    # ========================================================
    # 12. TOP NHÂN VIÊN ĐI MUỘN
    # ========================================================

    top_nv_di_muon = (
        cham_cong_nv
        .sort_values(
            [
                "tong_phut_di_muon",
                "so_luot_di_muon"
            ],
            ascending=False
        )
        .head(20)
    )


    print("\nTop 20 nhân viên theo tổng phút đi muộn:")

    print(
        top_nv_di_muon[
            [
                "employee_id",
                "name",
                "department_name",
                "tong_phut_di_muon",
                "so_luot_di_muon",
                "ty_le_di_muon"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # 13. CHẤM CÔNG THEO PHÒNG BAN
    # ========================================================

    cham_cong_pb = (
        cham_cong_nv
        .groupby(
            [
                "department_id",
                "department_name"
            ],
            dropna=False
        )
        .agg(
            so_nhan_vien=(
                "employee_id",
                "nunique"
            ),
            tong_luot_cham_cong=(
                "so_luot_cham_cong",
                "sum"
            ),
            tong_gio_lam=(
                "tong_gio_lam",
                "sum"
            ),
            tong_phut_di_muon=(
                "tong_phut_di_muon",
                "sum"
            ),
            so_luot_di_muon=(
                "so_luot_di_muon",
                "sum"
            )
        )
        .reset_index()
    )


    cham_cong_pb["ty_le_di_muon"] = (
        cham_cong_pb["so_luot_di_muon"]
        / cham_cong_pb["tong_luot_cham_cong"]
        * 100
    ).round(2)


    cham_cong_pb = cham_cong_pb.sort_values(
        "tong_phut_di_muon",
        ascending=False
    )


    print("\nChấm công theo phòng ban:")

    print(
        cham_cong_pb.to_string(
            index=False
        )
    )


else:

    tong_luot_cc = 0
    tong_gio = 0
    gio_tb_luot = 0
    tong_phut_muon = 0
    so_luot_muon = 0
    ty_le_luot_muon = 0

    cham_cong_ngay = pd.DataFrame()
    cham_cong_nv = pd.DataFrame()
    top_nv_di_muon = pd.DataFrame()
    cham_cong_pb = pd.DataFrame()


# ============================================================
# 14. NUMPY - THỐNG KÊ GIỜ LÀM
# ============================================================

print("\n" + "=" * 70)
print("7. THỐNG KÊ NUMPY")
print("=" * 70)


if len(cham_cong) > 0:

    arr_gio = (
        cham_cong["worked_hours"]
        .dropna()
        .to_numpy()
    )

    print(
        "Số giá trị:",
        len(arr_gio)
    )

    print(
        "Mean:",
        round(np.mean(arr_gio), 2)
    )

    print(
        "Median:",
        round(np.median(arr_gio), 2)
    )

    print(
        "Min:",
        round(np.min(arr_gio), 2)
    )

    print(
        "Max:",
        round(np.max(arr_gio), 2)
    )

    print(
        "Std:",
        round(np.std(arr_gio), 2)
    )

    print(
        "P25:",
        round(np.percentile(arr_gio, 25), 2)
    )

    print(
        "P75:",
        round(np.percentile(arr_gio, 75), 2)
    )


# ============================================================
# 15. KPI TỔNG HỢP
# ============================================================

print("\n" + "=" * 70)
print("8. KPI TỔNG HỢP")
print("=" * 70)


kpi = pd.DataFrame(
    [
        {
            "chi_so": "Tổng nhân viên",
            "gia_tri": tong_nhan_vien
        },
        {
            "chi_so": "Nhân viên active",
            "gia_tri": so_active
        },
        {
            "chi_so": "Nhân viên inactive",
            "gia_tri": so_inactive
        },
        {
            "chi_so": "Tổng phòng ban",
            "gia_tri": len(phong_ban)
        },
        {
            "chi_so": "Tổng vị trí",
            "gia_tri": len(vi_tri)
        },
        {
            "chi_so": "Tổng hợp đồng",
            "gia_tri": tong_hop_dong
        },
        {
            "chi_so": "Hợp đồng không có date_end",
            "gia_tri": (
                hop_dong["date_end"].isna().sum()
                if "date_end" in hop_dong.columns
                else np.nan
            )
        },
        {
            "chi_so": "Tổng đơn nghỉ phép",
            "gia_tri": tong_don_nghi
        },
        {
            "chi_so": "Tổng ngày nghỉ phép",
            "gia_tri": tong_ngay_nghi
        },
        {
            "chi_so": "Tổng lượt chấm công",
            "gia_tri": tong_luot_cc
        },
        {
            "chi_so": "Tổng giờ làm",
            "gia_tri": round(tong_gio, 2)
        },
        {
            "chi_so": "Giờ làm trung bình / lượt",
            "gia_tri": round(gio_tb_luot, 2)
        },
        {
            "chi_so": "Tổng phút đi muộn",
            "gia_tri": round(tong_phut_muon, 2)
        },
        {
            "chi_so": "Số lượt đi muộn",
            "gia_tri": so_luot_muon
        },
        {
            "chi_so": "Tỷ lệ lượt đi muộn (%)",
            "gia_tri": round(ty_le_luot_muon, 2)
        }
    ]
)


print(
    kpi.to_string(
        index=False
    )
)


# ============================================================
# 16. XUẤT KẾT QUẢ
# ============================================================

print("\n" + "=" * 70)
print("9. XUẤT KẾT QUẢ PHÂN TÍCH")
print("=" * 70)


def xuat_csv(df, ten_file):

    duong_dan = (
        thu_muc_phan_tich / ten_file
    )

    df.to_csv(
        duong_dan,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Đã xuất: {duong_dan}"
    )


xuat_csv(
    kpi,
    "kpi_tong_hop.csv"
)

xuat_csv(
    thong_ke_gender,
    "nhan_vien_theo_gioi_tinh.csv"
)

xuat_csv(
    thong_ke_loai_nv,
    "nhan_vien_theo_loai.csv"
)

xuat_csv(
    thong_ke_phong_ban,
    "nhan_vien_theo_phong_ban.csv"
)

xuat_csv(
    thong_ke_vi_tri,
    "nhan_vien_theo_vi_tri.csv"
)

xuat_csv(
    hop_dong_moi_nv,
    "hop_dong_theo_nhan_vien.csv"
)

xuat_csv(
    thong_ke_state_hd,
    "hop_dong_theo_trang_thai.csv"
)

xuat_csv(
    nghi_phep_nv,
    "nghi_phep_theo_nhan_vien.csv"
)

xuat_csv(
    cham_cong_ngay,
    "cham_cong_theo_ngay.csv"
)

xuat_csv(
    cham_cong_nv,
    "cham_cong_theo_nhan_vien.csv"
)

xuat_csv(
    top_nv_di_muon,
    "top_nhan_vien_di_muon.csv"
)

xuat_csv(
    cham_cong_pb,
    "cham_cong_theo_phong_ban.csv"
)


# ============================================================
# 17. KẾT THÚC
# ============================================================

print("\n" + "=" * 70)
print("HOÀN THÀNH PHÂN TÍCH HR")
print("=" * 70)

print(
    "\nThư mục kết quả:"
)

print(
    thu_muc_phan_tich
)