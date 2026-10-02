from pathlib import Path
import pandas as pd
import numpy as np


print("=" * 70)
print("2. KIỂM TRA CHẤT LƯỢNG DỮ LIỆU HR")
print("=" * 70)


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

thu_muc = Path(__file__).parent
thu_muc_csv = thu_muc / "csv"


# ============================================================
# 2. ĐỌC DỮ LIỆU
# ============================================================

def doc_csv(ten_file):
    duong_dan = thu_muc_csv / ten_file

    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {duong_dan}"
        )

    df = pd.read_csv(
        duong_dan,
        encoding="utf-8-sig"
    )

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.strip()

    # Chuẩn hóa chuỗi
    for cot in df.select_dtypes(include="object").columns:
        df[cot] = df[cot].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

        df[cot] = df[cot].replace(
            ["", " ", "nan", "NaN", "NULL", "null"],
            np.nan
        )

    return df


nhan_vien = doc_csv("nhan_vien.csv")
phong_ban = doc_csv("phong_ban.csv")
vi_tri = doc_csv("vi_tri.csv")
hop_dong = doc_csv("hop_dong.csv")
cham_cong = doc_csv("cham_cong.csv")
nghi_phep = doc_csv("nghi_phep.csv")


# ============================================================
# 3. HÀM IN TIÊU ĐỀ
# ============================================================

def tieu_de(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


# ============================================================
# 4. KIỂM TRA NHÂN VIÊN
# ============================================================

tieu_de("1. CHẤT LƯỢNG DỮ LIỆU NHÂN VIÊN")


print("Tổng nhân viên:", len(nhan_vien))


# ID
if "id" in nhan_vien.columns:

    print(
        "ID thiếu:",
        nhan_vien["id"].isna().sum()
    )

    print(
        "ID trùng:",
        nhan_vien["id"].duplicated().sum()
    )


# Tên
if "name" in nhan_vien.columns:

    print(
        "Tên thiếu:",
        nhan_vien["name"].isna().sum()
    )

    print(
        "Tên trùng:",
        nhan_vien["name"].duplicated().sum()
    )


# Department
if "department_id" in nhan_vien.columns:

    nv_khong_phong_ban = nhan_vien[
        nhan_vien["department_id"].isna()
    ]

    print(
        "Nhân viên không có phòng ban:",
        len(nv_khong_phong_ban)
    )

    if len(nv_khong_phong_ban) > 0:

        print("\nDanh sách nhân viên không có phòng ban:")

        cot_hien_thi = [
            cot for cot in
            ["id", "name", "job_title", "employee_code"]
            if cot in nv_khong_phong_ban.columns
        ]

        print(
            nv_khong_phong_ban[cot_hien_thi]
            .to_string(index=False)
        )


# Job
if "job_id" in nhan_vien.columns:

    print(
        "Nhân viên không có job_id:",
        nhan_vien["job_id"].isna().sum()
    )


# ============================================================
# 5. KIỂM TRA PHÒNG BAN
# ============================================================

tieu_de("2. CHẤT LƯỢNG DỮ LIỆU PHÒNG BAN")


print("Tổng phòng ban:", len(phong_ban))


if "department_id" in phong_ban.columns:

    print(
        "Department ID thiếu:",
        phong_ban["department_id"].isna().sum()
    )

    print(
        "Department ID trùng:",
        phong_ban["department_id"].duplicated().sum()
    )


if "department_name" in phong_ban.columns:

    print(
        "Tên phòng ban thiếu:",
        phong_ban["department_name"].isna().sum()
    )


# Kiểm tra parent_id
if "parent_id" in phong_ban.columns:

    print(
        "Phòng ban không có parent_id:",
        phong_ban["parent_id"].isna().sum()
    )

    parent_ids = set(
        pd.to_numeric(
            phong_ban["id"],
            errors="coerce"
        ).dropna()
    )

    parent = pd.to_numeric(
        phong_ban["parent_id"],
        errors="coerce"
    )

    parent_khong_ton_tai = (
        ~parent.isna()
        & ~parent.isin(parent_ids)
    )

    print(
        "parent_id không tồn tại:",
        parent_khong_ton_tai.sum()
    )


# ============================================================
# 6. KIỂM TRA VỊ TRÍ
# ============================================================

tieu_de("3. CHẤT LƯỢNG DỮ LIỆU VỊ TRÍ")


print("Tổng vị trí:", len(vi_tri))


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

    print(
        "Department ID thiếu:",
        vi_tri["department_id"].isna().sum()
    )


if "department_name" in vi_tri.columns:

    print(
        "Department name thiếu:",
        vi_tri["department_name"].isna().sum()
    )

    vt_thieu_ten_pb = vi_tri[
        vi_tri["department_name"].isna()
    ]

    if len(vt_thieu_ten_pb) > 0:

        print("\nVị trí thiếu department_name:")

        cot_hien_thi = [
            cot for cot in
            [
                "job_id",
                "job_position",
                "department_id"
            ]
            if cot in vt_thieu_ten_pb.columns
        ]

        print(
            vt_thieu_ten_pb[cot_hien_thi]
            .to_string(index=False)
        )


# ============================================================
# 7. KIỂM TRA HỢP ĐỒNG
# ============================================================

tieu_de("4. CHẤT LƯỢNG DỮ LIỆU HỢP ĐỒNG")


print("Tổng hợp đồng:", len(hop_dong))


# ID nhân viên
employee_ids = set(
    pd.to_numeric(
        nhan_vien["id"],
        errors="coerce"
    ).dropna()
)


if "employee_id" in hop_dong.columns:

    employee_contract = pd.to_numeric(
        hop_dong["employee_id"],
        errors="coerce"
    )

    print(
        "Employee ID thiếu:",
        employee_contract.isna().sum()
    )

    orphan_contract = (
        ~employee_contract.isna()
        & ~employee_contract.isin(employee_ids)
    )

    print(
        "Hợp đồng không có nhân viên:",
        orphan_contract.sum()
    )


# Nhiều hợp đồng
if "employee_id" in hop_dong.columns:

    so_hop_dong = (
        hop_dong
        .groupby("employee_id")
        .size()
    )

    nv_nhieu_hd = so_hop_dong[
        so_hop_dong > 1
    ]

    print(
        "Nhân viên có nhiều hơn 1 hợp đồng:",
        len(nv_nhieu_hd)
    )

    if len(nv_nhieu_hd) > 0:

        print("\nDanh sách nhân viên có nhiều hợp đồng:")

        print(
            nv_nhieu_hd
            .sort_values(ascending=False)
            .to_string()
        )


# Wage
if "wage" in hop_dong.columns:

    wage = pd.to_numeric(
        hop_dong["wage"],
        errors="coerce"
    )

    print(
        "\nwage thiếu:",
        wage.isna().sum()
    )

    print(
        "wage = 0:",
        (wage == 0).sum()
    )

    print(
        "wage > 0:",
        (wage > 0).sum()
    )

    print(
        "wage < 0:",
        (wage < 0).sum()
    )


# Date start
if "date_start" in hop_dong.columns:

    date_start = pd.to_datetime(
        hop_dong["date_start"],
        errors="coerce"
    )

    print(
        "\ndate_start thiếu:",
        date_start.isna().sum()
    )


# Date end
if "date_end" in hop_dong.columns:

    date_end = pd.to_datetime(
        hop_dong["date_end"],
        errors="coerce"
    )

    print(
        "date_end thiếu:",
        date_end.isna().sum()
    )

    if "date_start" in hop_dong.columns:

        date_sai = (
            (date_end < date_start)
            & date_end.notna()
            & date_start.notna()
        )

        print(
            "date_end trước date_start:",
            date_sai.sum()
        )


# State
if "state" in hop_dong.columns:

    print("\nPhân bố trạng thái hợp đồng:")

    print(
        hop_dong["state"]
        .fillna("Chưa xác định")
        .value_counts()
        .to_string()
    )


# ============================================================
# 8. KIỂM TRA CHẤM CÔNG
# ============================================================

tieu_de("5. CHẤT LƯỢNG DỮ LIỆU CHẤM CÔNG")


print("Tổng dòng chấm công:", len(cham_cong))


if len(cham_cong) > 0:

    # Employee
    if "employee_id" in cham_cong.columns:

        attendance_employee = pd.to_numeric(
            cham_cong["employee_id"],
            errors="coerce"
        )

        print(
            "Employee ID thiếu:",
            attendance_employee.isna().sum()
        )

        attendance_orphan = (
            ~attendance_employee.isna()
            & ~attendance_employee.isin(employee_ids)
        )

        print(
            "Chấm công không có nhân viên:",
            attendance_orphan.sum()
        )


    # Check in
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


    # Check out
    if "check_out" in cham_cong.columns:

        check_out = pd.to_datetime(
            cham_cong["check_out"],
            errors="coerce"
        )

        print(
            "check_out thiếu:",
            check_out.isna().sum()
        )

        sai_gio = (
            (check_out < check_in)
            & check_out.notna()
            & check_in.notna()
        )

        print(
            "check_out trước check_in:",
            sai_gio.sum()
        )


    # Worked hours
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
            "worked_hours > 24:",
            (worked_hours > 24).sum()
        )

        print(
            "Tổng giờ làm:",
            round(worked_hours.sum(), 2)
        )

        print(
            "Trung bình giờ / lượt:",
            round(worked_hours.mean(), 2)
        )


    # Đi muộn
    if "so_phut_di_muon" in cham_cong.columns:

        phut_muon = pd.to_numeric(
            cham_cong["so_phut_di_muon"],
            errors="coerce"
        )

        print(
            "\nPhút đi muộn thiếu:",
            phut_muon.isna().sum()
        )

        print(
            "Phút đi muộn âm:",
            (phut_muon < 0).sum()
        )

        print(
            "Tổng phút đi muộn:",
            round(phut_muon.sum(), 2)
        )

        print(
            "Số lượt đi muộn:",
            (phut_muon > 0).sum()
        )

        print(
            "Trung bình phút đi muộn / lượt có đi muộn:",
            round(
                phut_muon[phut_muon > 0].mean(),
                2
            )
        )


    # Trạng thái
    if "trang_thai_cham_cong" in cham_cong.columns:

        print("\nPhân bố trạng thái:")

        print(
            cham_cong[
                "trang_thai_cham_cong"
            ]
            .fillna("Chưa xác định")
            .value_counts()
            .to_string()
        )


    # Dòng trùng
    print(
        "\nDòng trùng toàn bộ:",
        cham_cong.duplicated().sum()
    )


    # Trùng employee + check_in
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

tieu_de("6. CHẤT LƯỢNG DỮ LIỆU NGHỈ PHÉP")


print("Tổng đơn nghỉ phép:", len(nghi_phep))


if len(nghi_phep) > 0:

    if "employee_id" in nghi_phep.columns:

        leave_employee = pd.to_numeric(
            nghi_phep["employee_id"],
            errors="coerce"
        )

        print(
            "Employee ID thiếu:",
            leave_employee.isna().sum()
        )

        leave_orphan = (
            ~leave_employee.isna()
            & ~leave_employee.isin(employee_ids)
        )

        print(
            "Nghỉ phép không có nhân viên:",
            leave_orphan.sum()
        )


    if "number_of_days" in nghi_phep.columns:

        days_leave = pd.to_numeric(
            nghi_phep["number_of_days"],
            errors="coerce"
        )

        print(
            "Số ngày nghỉ thiếu:",
            days_leave.isna().sum()
        )

        print(
            "Số ngày nghỉ âm:",
            (days_leave < 0).sum()
        )

        print(
            "Tổng ngày nghỉ:",
            round(days_leave.sum(), 2)
        )


    if (
        "date_from" in nghi_phep.columns
        and "date_to" in nghi_phep.columns
    ):

        date_from = pd.to_datetime(
            nghi_phep["date_from"],
            errors="coerce"
        )

        date_to = pd.to_datetime(
            nghi_phep["date_to"],
            errors="coerce"
        )

        print(
            "date_from thiếu:",
            date_from.isna().sum()
        )

        print(
            "date_to thiếu:",
            date_to.isna().sum()
        )

        sai_ngay = (
            (date_to < date_from)
            & date_to.notna()
            & date_from.notna()
        )

        print(
            "date_to trước date_from:",
            sai_ngay.sum()
        )


    if "state" in nghi_phep.columns:

        print("\nPhân bố trạng thái nghỉ phép:")

        print(
            nghi_phep["state"]
            .fillna("Chưa xác định")
            .value_counts()
            .to_string()
        )


# ============================================================
# 10. KIỂM TRA DÒNG TRÙNG TOÀN BỘ
# ============================================================

tieu_de("7. KIỂM TRA DÒNG TRÙNG")


cac_bang = {
    "nhan_vien": nhan_vien,
    "phong_ban": phong_ban,
    "vi_tri": vi_tri,
    "hop_dong": hop_dong,
    "cham_cong": cham_cong,
    "nghi_phep": nghi_phep,
}


for ten, df in cac_bang.items():

    print(
        f"{ten:12}: {df.duplicated().sum()} dòng trùng"
    )


# ============================================================
# 11. TỔNG HỢP CHẤT LƯỢNG
# ============================================================

tieu_de("8. TỔNG HỢP")


print("Số bảng dữ liệu:", len(cac_bang))

print(
    "Tổng số dòng:",
    sum(len(df) for df in cac_bang.values())
)


print("\nCác vấn đề cần chú ý:")

print("1. Không tự động xóa nhân viên không có phòng ban.")

print("2. Không tự động xóa nhân viên có nhiều hợp đồng.")

print("3. Không tự động sửa wage = 0.")

print("4. Không tự động điền date_end bị thiếu.")

print("5. Không tự động xóa dòng chấm công.")

print("6. Không tự động điền dữ liệu thiếu bằng dữ liệu giả.")


# ============================================================
# 12. KẾT THÚC
# ============================================================

print("\n" + "=" * 70)
print("HOÀN THÀNH KIỂM TRA CHẤT LƯỢNG")
print("=" * 70)