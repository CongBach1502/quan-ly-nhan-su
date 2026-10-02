from pathlib import Path
import pandas as pd
import numpy as np


print("=" * 70)
print("1. KIỂM TRA DỮ LIỆU HR")
print("=" * 70)


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

thu_muc = Path(__file__).parent
thu_muc_csv = thu_muc / "csv"


# ============================================================
# 2. ĐỌC 6 FILE CSV
# ============================================================

def doc_csv(ten_file):
    duong_dan = thu_muc_csv / ten_file

    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {duong_dan}"
        )

    return pd.read_csv(
        duong_dan,
        encoding="utf-8-sig"
    )


nhan_vien = doc_csv("nhan_vien.csv")
phong_ban = doc_csv("phong_ban.csv")
vi_tri = doc_csv("vi_tri.csv")
hop_dong = doc_csv("hop_dong.csv")
cham_cong = doc_csv("cham_cong.csv")
nghi_phep = doc_csv("nghi_phep.csv")


# ============================================================
# 3. TỔNG QUAN
# ============================================================

print("\n" + "=" * 70)
print("TỔNG QUAN DỮ LIỆU")
print("=" * 70)

print(f"Nhân viên : {len(nhan_vien)} dòng, {len(nhan_vien.columns)} cột")
print(f"Phòng ban : {len(phong_ban)} dòng, {len(phong_ban.columns)} cột")
print(f"Vị trí    : {len(vi_tri)} dòng, {len(vi_tri.columns)} cột")
print(f"Hợp đồng  : {len(hop_dong)} dòng, {len(hop_dong.columns)} cột")
print(f"Chấm công : {len(cham_cong)} dòng, {len(cham_cong.columns)} cột")
print(f"Nghỉ phép : {len(nghi_phep)} dòng, {len(nghi_phep.columns)} cột")


# ============================================================
# 4. KIỂM TRA NHÂN VIÊN
# ============================================================

print("\n" + "=" * 70)
print("1. KIỂM TRA NHÂN VIÊN")
print("=" * 70)


if "id" in nhan_vien.columns:

    print("Tổng ID:", nhan_vien["id"].notna().sum())

    print(
        "ID thiếu:",
        nhan_vien["id"].isna().sum()
    )

    print(
        "ID trùng:",
        nhan_vien["id"].duplicated().sum()
    )

else:
    print("WARNING: Không có cột id")


if "name" in nhan_vien.columns:

    print(
        "Tên nhân viên thiếu:",
        nhan_vien["name"].isna().sum()
    )

    print(
        "Tên nhân viên trùng:",
        nhan_vien["name"].duplicated().sum()
    )


if "department_id" in nhan_vien.columns:

    so_nv_khong_phong = (
        nhan_vien["department_id"].isna().sum()
    )

    print(
        "Nhân viên không có phòng ban:",
        so_nv_khong_phong
    )


# ============================================================
# 5. KIỂM TRA PHÒNG BAN
# ============================================================

print("\n" + "=" * 70)
print("2. KIỂM TRA PHÒNG BAN")
print("=" * 70)


if "department_id" in phong_ban.columns:

    print(
        "Department ID thiếu:",
        phong_ban["department_id"].isna().sum()
    )

    print(
        "Department ID trùng:",
        phong_ban["department_id"].duplicated().sum()
    )


# Danh sách department_id hợp lệ

if "department_id" in phong_ban.columns:

    department_ids = set(
        pd.to_numeric(
            phong_ban["department_id"],
            errors="coerce"
        ).dropna()
    )

else:

    department_ids = set()


# Kiểm tra department của nhân viên

if "department_id" in nhan_vien.columns:

    department_nv = pd.to_numeric(
        nhan_vien["department_id"],
        errors="coerce"
    )

    department_khong_ton_tai = (
        ~department_nv.isna()
        & ~department_nv.isin(department_ids)
    )

    print(
        "Nhân viên có department_id không tồn tại:",
        department_khong_ton_tai.sum()
    )


# ============================================================
# 6. KIỂM TRA VỊ TRÍ
# ============================================================

print("\n" + "=" * 70)
print("3. KIỂM TRA VỊ TRÍ")
print("=" * 70)


print("Tổng số vị trí:", len(vi_tri))


if len(vi_tri) == 0:

    print("WARNING: vi_tri.csv đang rỗng.")

else:

    if "job_id" in vi_tri.columns:

        print(
            "Job ID thiếu:",
            vi_tri["job_id"].isna().sum()
        )

        print(
            "Job ID trùng:",
            vi_tri["job_id"].duplicated().sum()
        )

    if "job_position" in vi_tri.columns:

        print(
            "Tên vị trí thiếu:",
            vi_tri["job_position"].isna().sum()
        )

    if "department_id" in vi_tri.columns:

        department_vi_tri = pd.to_numeric(
            vi_tri["department_id"],
            errors="coerce"
        )

        department_khong_ton_tai = (
            ~department_vi_tri.isna()
            & ~department_vi_tri.isin(department_ids)
        )

        print(
            "Vị trí có department_id không tồn tại:",
            department_khong_ton_tai.sum()
        )

    if "department_name" in vi_tri.columns:

        print(
            "Tên phòng ban trong vị trí thiếu:",
            vi_tri["department_name"].isna().sum()
        )


# ============================================================
# 7. KIỂM TRA HỢP ĐỒNG
# ============================================================

print("\n" + "=" * 70)
print("4. KIỂM TRA HỢP ĐỒNG")
print("=" * 70)


print("Tổng số hợp đồng:", len(hop_dong))


if "employee_id" in hop_dong.columns:

    employee_ids = set(
        pd.to_numeric(
            nhan_vien["id"],
            errors="coerce"
        ).dropna()
    )

    contract_employee = pd.to_numeric(
        hop_dong["employee_id"],
        errors="coerce"
    )

    contract_khong_nv = (
        ~contract_employee.isna()
        & ~contract_employee.isin(employee_ids)
    )

    print(
        "Hợp đồng không tìm thấy nhân viên:",
        contract_khong_nv.sum()
    )


if "employee_id" in hop_dong.columns:

    so_hop_dong_nv = (
        hop_dong
        .groupby("employee_id")
        .size()
    )

    print(
        "Nhân viên có nhiều hơn 1 hợp đồng:",
        (so_hop_dong_nv > 1).sum()
    )


if "wage" in hop_dong.columns:

    wage = pd.to_numeric(
        hop_dong["wage"],
        errors="coerce"
    )

    print(
        "wage thiếu:",
        wage.isna().sum()
    )

    print(
        "wage = 0:",
        (wage == 0).sum()
    )


if "date_start" in hop_dong.columns:

    date_start = pd.to_datetime(
        hop_dong["date_start"],
        errors="coerce"
    )

    print(
        "date_start thiếu:",
        date_start.isna().sum()
    )

else:

    date_start = pd.Series(
        pd.NaT,
        index=hop_dong.index
    )


if "date_end" in hop_dong.columns:

    date_end = pd.to_datetime(
        hop_dong["date_end"],
        errors="coerce"
    )

    print(
        "date_end thiếu:",
        date_end.isna().sum()
    )

    ngay_khong_hop_le = (
        (date_end < date_start)
        & date_end.notna()
        & date_start.notna()
    )

    print(
        "date_end trước date_start:",
        ngay_khong_hop_le.sum()
    )


# ============================================================
# 8. KIỂM TRA CHẤM CÔNG
# ============================================================

print("\n" + "=" * 70)
print("5. KIỂM TRA CHẤM CÔNG")
print("=" * 70)


print(
    "Tổng số dòng chấm công:",
    len(cham_cong)
)


if len(cham_cong) == 0:

    print("WARNING: cham_cong.csv đang rỗng.")

else:

    # --------------------------------------------------------
    # Employee ID
    # --------------------------------------------------------

    if "employee_id" in cham_cong.columns:

        attendance_employee = pd.to_numeric(
            cham_cong["employee_id"],
            errors="coerce"
        )

        attendance_khong_nv = (
            ~attendance_employee.isna()
            & ~attendance_employee.isin(employee_ids)
        )

        print(
            "Chấm công không tìm thấy nhân viên:",
            attendance_khong_nv.sum()
        )

        print(
            "Employee ID thiếu:",
            attendance_employee.isna().sum()
        )


    # --------------------------------------------------------
    # Check in
    # --------------------------------------------------------

    if "check_in" in cham_cong.columns:

        check_in = pd.to_datetime(
            cham_cong["check_in"],
            errors="coerce"
        )

        print(
            "check_in thiếu:",
            check_in.isna().sum()
        )

    else:

        check_in = pd.Series(
            pd.NaT,
            index=cham_cong.index
        )

        print(
            "WARNING: Không có cột check_in"
        )


    # --------------------------------------------------------
    # Check out
    # --------------------------------------------------------

    if "check_out" in cham_cong.columns:

        check_out = pd.to_datetime(
            cham_cong["check_out"],
            errors="coerce"
        )

        print(
            "check_out thiếu:",
            check_out.isna().sum()
        )

        check_out_truoc_check_in = (
            (check_out < check_in)
            & check_out.notna()
            & check_in.notna()
        )

        print(
            "check_out trước check_in:",
            check_out_truoc_check_in.sum()
        )

    else:

        print(
            "WARNING: Không có cột check_out"
        )


    # --------------------------------------------------------
    # Worked hours
    # --------------------------------------------------------

    if "worked_hours" in cham_cong.columns:

        worked_hours = pd.to_numeric(
            cham_cong["worked_hours"],
            errors="coerce"
        )

        print(
            "worked_hours thiếu:",
            worked_hours.isna().sum()
        )

        print(
            "worked_hours âm:",
            (worked_hours < 0).sum()
        )

        print(
            "worked_hours = 0:",
            (worked_hours == 0).sum()
        )

        print(
            "Tổng worked_hours:",
            round(worked_hours.sum(), 2)
        )

        print(
            "Trung bình worked_hours:",
            round(worked_hours.mean(), 2)
        )


    # --------------------------------------------------------
    # Đi muộn
    # --------------------------------------------------------

    if "so_phut_di_muon" in cham_cong.columns:

        phut_di_muon = pd.to_numeric(
            cham_cong["so_phut_di_muon"],
            errors="coerce"
        )

        print(
            "so_phut_di_muon thiếu:",
            phut_di_muon.isna().sum()
        )

        print(
            "Tổng phút đi muộn:",
            round(phut_di_muon.sum(), 2)
        )

        print(
            "Số lượt có đi muộn:",
            (phut_di_muon > 0).sum()
        )


    # --------------------------------------------------------
    # Trạng thái chấm công
    # --------------------------------------------------------

    if "trang_thai_cham_cong" in cham_cong.columns:

        print("\nPhân bố trạng thái chấm công:")

        print(
            cham_cong[
                "trang_thai_cham_cong"
            ]
            .fillna("Chưa xác định")
            .value_counts()
            .to_string()
        )


    # --------------------------------------------------------
    # Dòng trùng
    # --------------------------------------------------------

    print(
        "\nDòng chấm công trùng toàn bộ:",
        cham_cong.duplicated().sum()
    )


    # --------------------------------------------------------
    # Trùng employee + check_in
    # --------------------------------------------------------

    if (
        "employee_id" in cham_cong.columns
        and "check_in" in cham_cong.columns
    ):

        temp = cham_cong[
            ["employee_id", "check_in"]
        ].copy()

        temp["employee_id"] = pd.to_numeric(
            temp["employee_id"],
            errors="coerce"
        )

        temp["check_in"] = pd.to_datetime(
            temp["check_in"],
            errors="coerce"
        )

        print(
            "Trùng employee_id + check_in:",
            temp.duplicated().sum()
        )


# ============================================================
# 9. KIỂM TRA NGHỈ PHÉP
# ============================================================

print("\n" + "=" * 70)
print("6. KIỂM TRA NGHỈ PHÉP")
print("=" * 70)


print(
    "Tổng số đơn nghỉ phép:",
    len(nghi_phep)
)


if len(nghi_phep) > 0:

    if "employee_id" in nghi_phep.columns:

        leave_employee = pd.to_numeric(
            nghi_phep["employee_id"],
            errors="coerce"
        )

        leave_khong_nv = (
            ~leave_employee.isna()
            & ~leave_employee.isin(employee_ids)
        )

        print(
            "Nghỉ phép không tìm thấy nhân viên:",
            leave_khong_nv.sum()
        )


    if (
        "date_from" in nghi_phep.columns
        and "date_to" in nghi_phep.columns
    ):

        leave_from = pd.to_datetime(
            nghi_phep["date_from"],
            errors="coerce"
        )

        leave_to = pd.to_datetime(
            nghi_phep["date_to"],
            errors="coerce"
        )

        print(
            "date_from thiếu:",
            leave_from.isna().sum()
        )

        print(
            "date_to thiếu:",
            leave_to.isna().sum()
        )

        leave_sai_ngay = (
            (leave_to < leave_from)
            & leave_to.notna()
            & leave_from.notna()
        )

        print(
            "date_to trước date_from:",
            leave_sai_ngay.sum()
        )


# ============================================================
# 10. NUMPY
# ============================================================

print("\n" + "=" * 70)
print("7. THỐNG KÊ BẰNG NUMPY")
print("=" * 70)


so_dong = np.array([
    len(nhan_vien),
    len(phong_ban),
    len(vi_tri),
    len(hop_dong),
    len(cham_cong),
    len(nghi_phep)
])


print("Số dòng 6 file:")
print(so_dong)

print(
    "Tổng số dòng:",
    so_dong.sum()
)

print(
    "Trung bình:",
    round(so_dong.mean(), 2)
)

print(
    "Lớn nhất:",
    so_dong.max()
)

print(
    "Nhỏ nhất:",
    so_dong.min()
)


# ============================================================
# 11. KẾT THÚC
# ============================================================

print("\n" + "=" * 70)
print("HOÀN THÀNH KIỂM TRA DỮ LIỆU")
print("=" * 70)