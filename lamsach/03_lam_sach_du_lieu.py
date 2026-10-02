from pathlib import Path
import pandas as pd
import numpy as np


print("=" * 70)
print("3. LÀM SẠCH DỮ LIỆU HR")
print("=" * 70)


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

thu_muc = Path(__file__).parent
thu_muc_csv = thu_muc / "csv"
thu_muc_output = thu_muc / "output"

# Tạo thư mục output nếu chưa có
thu_muc_output.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. DANH SÁCH FILE
# ============================================================

files = {
    "nhan_vien": "nhan_vien.csv",
    "phong_ban": "phong_ban.csv",
    "vi_tri": "vi_tri.csv",
    "hop_dong": "hop_dong.csv",
    "cham_cong": "cham_cong.csv",
    "nghi_phep": "nghi_phep.csv",
}


# ============================================================
# 3. HÀM ĐỌC CSV
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

    return df


# ============================================================
# 4. HÀM LÀM SẠCH CƠ BẢN
# ============================================================

def lam_sach_co_ban(df):

    df = df.copy()

    # --------------------------------------------------------
    # Chuẩn hóa tên cột
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Chuẩn hóa dữ liệu dạng text
    # --------------------------------------------------------

    cot_text = df.select_dtypes(
        include=["object"]
    ).columns

    for cot in cot_text:

        df[cot] = df[cot].apply(
            lambda x:
            x.strip()
            if isinstance(x, str)
            else x
        )

        # Chuỗi rỗng -> NaN
        df[cot] = df[cot].replace(
            r"^\s*$",
            np.nan,
            regex=True
        )

    # --------------------------------------------------------
    # Xóa dòng trùng toàn bộ
    # --------------------------------------------------------

    so_dong_truoc = len(df)

    df = df.drop_duplicates().copy()

    so_dong_sau = len(df)

    print(
        f"  Xóa dòng trùng: "
        f"{so_dong_truoc - so_dong_sau}"
    )

    return df


# ============================================================
# 5. ĐỌC VÀ LÀM SẠCH 6 FILE
# ============================================================

data = {}

for ten, ten_file in files.items():

    print("\n" + "-" * 70)
    print(f"Đang xử lý: {ten_file}")

    df = doc_csv(ten_file)

    print(
        "  Số dòng ban đầu:",
        len(df)
    )

    df = lam_sach_co_ban(df)

    print(
        "  Số dòng sau làm sạch cơ bản:",
        len(df)
    )

    data[ten] = df


# ============================================================
# 6. GÁN BIẾN
# ============================================================

nhan_vien = data["nhan_vien"]
phong_ban = data["phong_ban"]
vi_tri = data["vi_tri"]
hop_dong = data["hop_dong"]
cham_cong = data["cham_cong"]
nghi_phep = data["nghi_phep"]


# ============================================================
# 7. CHUẨN HÓA CỘT SỐ
# ============================================================

print("\n" + "=" * 70)
print("CHUẨN HÓA CỘT SỐ")
print("=" * 70)


# ------------------------------------------------------------
# Nhân viên
# ------------------------------------------------------------

cac_cot_so_nv = [
    "id",
    "resource_id",
    "company_id",
    "resource_calendar_id",
    "department_id",
    "job_id",
    "address_id",
    "work_contact_id",
    "work_location_id",
    "user_id",
    "parent_id",
    "coach_id",
    "address_home_id",
    "country_id",
    "children",
    "bank_account_id",
    "km_home_work",
    "departure_reason_id",
    "create_uid",
    "write_uid",
    "color",
    "last_attendance_id",
    "leave_manager_id",
    "contract_id",
]


for cot in cac_cot_so_nv:

    if cot in nhan_vien.columns:

        nhan_vien[cot] = pd.to_numeric(
            nhan_vien[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Phòng ban
# ------------------------------------------------------------

for cot in [
    "department_id",
    "parent_id",
]:

    if cot in phong_ban.columns:

        phong_ban[cot] = pd.to_numeric(
            phong_ban[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Vị trí
# ------------------------------------------------------------

for cot in [
    "job_id",
    "department_id",
]:

    if cot in vi_tri.columns:

        vi_tri[cot] = pd.to_numeric(
            vi_tri[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Hợp đồng
# ------------------------------------------------------------

for cot in [
    "contract_id",
    "employee_id",
    "contract_type_id",
    "wage",
]:

    if cot in hop_dong.columns:

        hop_dong[cot] = pd.to_numeric(
            hop_dong[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Chấm công
# ------------------------------------------------------------

for cot in [
    "id",
    "employee_id",
    "create_uid",
    "write_uid",
    "worked_hours",
    "so_phut_di_muon",
]:

    if cot in cham_cong.columns:

        cham_cong[cot] = pd.to_numeric(
            cham_cong[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Nghỉ phép
# ------------------------------------------------------------

for cot in [
    "leave_id",
    "employee_id",
    "holiday_status_id",
    "number_of_days",
]:

    if cot in nghi_phep.columns:

        nghi_phep[cot] = pd.to_numeric(
            nghi_phep[cot],
            errors="coerce"
        )


# ============================================================
# 8. CHUẨN HÓA NGÀY THÁNG
# ============================================================

print("\n" + "=" * 70)
print("CHUẨN HÓA NGÀY THÁNG")
print("=" * 70)


# ------------------------------------------------------------
# Nhân viên
# ------------------------------------------------------------

cac_cot_ngay_nv = [
    "spouse_birthdate",
    "birthday",
    "visa_expire",
    "work_permit_expiration_date",
    "departure_date",
    "create_date",
    "write_date",
    "last_check_in",
    "last_check_out",
    "first_contract_date",
]


for cot in cac_cot_ngay_nv:

    if cot in nhan_vien.columns:

        nhan_vien[cot] = pd.to_datetime(
            nhan_vien[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Hợp đồng
# ------------------------------------------------------------

for cot in [
    "date_start",
    "date_end",
]:

    if cot in hop_dong.columns:

        hop_dong[cot] = pd.to_datetime(
            hop_dong[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Chấm công
# ------------------------------------------------------------

for cot in [
    "check_in",
    "check_out",
    "create_date",
    "write_date",
]:

    if cot in cham_cong.columns:

        cham_cong[cot] = pd.to_datetime(
            cham_cong[cot],
            errors="coerce"
        )


# ------------------------------------------------------------
# Nghỉ phép
# ------------------------------------------------------------

for cot in [
    "request_date_from",
    "request_date_to",
    "date_from",
    "date_to",
]:

    if cot in nghi_phep.columns:

        nghi_phep[cot] = pd.to_datetime(
            nghi_phep[cot],
            errors="coerce"
        )


# ============================================================
# 9. KIỂM TRA SAU KHI LÀM SẠCH
# ============================================================

print("\n" + "=" * 70)
print("KIỂM TRA SAU KHI LÀM SẠCH")
print("=" * 70)


# ------------------------------------------------------------
# Nhân viên
# ------------------------------------------------------------

print("\n1. NHÂN VIÊN")

print(
    "Số dòng:",
    len(nhan_vien)
)

print(
    "ID thiếu:",
    nhan_vien["id"].isna().sum()
    if "id" in nhan_vien.columns
    else "Không có cột id"
)

print(
    "Tên thiếu:",
    nhan_vien["name"].isna().sum()
    if "name" in nhan_vien.columns
    else "Không có cột name"
)

print(
    "Department thiếu:",
    nhan_vien["department_id"].isna().sum()
    if "department_id" in nhan_vien.columns
    else "Không có cột department_id"
)


# ------------------------------------------------------------
# Phòng ban
# ------------------------------------------------------------

print("\n2. PHÒNG BAN")

print(
    "Số dòng:",
    len(phong_ban)
)

print(
    "Department ID thiếu:",
    phong_ban["department_id"].isna().sum()
    if "department_id" in phong_ban.columns
    else "Không có cột department_id"
)


# ------------------------------------------------------------
# Vị trí
# ------------------------------------------------------------

print("\n3. VỊ TRÍ")

print(
    "Số dòng:",
    len(vi_tri)
)

print(
    "Job ID thiếu:",
    vi_tri["job_id"].isna().sum()
    if "job_id" in vi_tri.columns
    else "Không có cột job_id"
)

print(
    "Department ID thiếu:",
    vi_tri["department_id"].isna().sum()
    if "department_id" in vi_tri.columns
    else "Không có cột department_id"
)


# ------------------------------------------------------------
# Hợp đồng
# ------------------------------------------------------------

print("\n4. HỢP ĐỒNG")

print(
    "Số dòng:",
    len(hop_dong)
)

if "wage" in hop_dong.columns:

    print(
        "wage = 0:",
        (
            hop_dong["wage"] == 0
        ).sum()
    )

if "date_end" in hop_dong.columns:

    print(
        "date_end thiếu:",
        hop_dong["date_end"].isna().sum()
    )


# ------------------------------------------------------------
# Chấm công
# ------------------------------------------------------------

print("\n5. CHẤM CÔNG")

print(
    "Số dòng:",
    len(cham_cong)
)

if "worked_hours" in cham_cong.columns:

    print(
        "worked_hours thiếu:",
        cham_cong["worked_hours"].isna().sum()
    )

    print(
        "worked_hours âm:",
        (
            cham_cong["worked_hours"] < 0
        ).sum()
    )

    print(
        "Tổng giờ làm:",
        round(
            cham_cong["worked_hours"].sum(),
            2
        )
    )


if "so_phut_di_muon" in cham_cong.columns:

    print(
        "Tổng phút đi muộn:",
        round(
            cham_cong["so_phut_di_muon"].sum(),
            2
        )
    )


# ------------------------------------------------------------
# Nghỉ phép
# ------------------------------------------------------------

print("\n6. NGHỈ PHÉP")

print(
    "Số dòng:",
    len(nghi_phep)
)

if "number_of_days" in nghi_phep.columns:

    print(
        "Tổng ngày nghỉ:",
        round(
            nghi_phep["number_of_days"].sum(),
            2
        )
    )


# ============================================================
# 10. GHI FILE OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("GHI FILE DỮ LIỆU ĐÃ LÀM SẠCH")
print("=" * 70)


for ten, df in data.items():

    ten_file = f"{ten}_sach.csv"

    duong_dan_output = (
        thu_muc_output / ten_file
    )

    # datetime -> chuỗi ISO để CSV dễ đọc lại
    df_xuat = df.copy()

    for cot in df_xuat.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df_xuat[cot]
        ):

            df_xuat[cot] = (
                df_xuat[cot]
                .dt.strftime("%Y-%m-%d %H:%M:%S")
            )

    df_xuat.to_csv(
        duong_dan_output,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Đã tạo: {duong_dan_output}"
    )


# ============================================================
# 11. NUMPY
# ============================================================

print("\n" + "=" * 70)
print("THỐNG KÊ NUMPY")
print("=" * 70)


so_dong = np.array([
    len(nhan_vien),
    len(phong_ban),
    len(vi_tri),
    len(hop_dong),
    len(cham_cong),
    len(nghi_phep),
])


print(
    "Số dòng:",
    so_dong
)

print(
    "Tổng:",
    so_dong.sum()
)

print(
    "Trung bình:",
    round(
        so_dong.mean(),
        2
    )
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
# 12. KẾT THÚC
# ============================================================

print("\n" + "=" * 70)
print("HOÀN THÀNH LÀM SẠCH DỮ LIỆU")
print("=" * 70)

print(
    "\nCác file đã làm sạch nằm tại:"
)

print(
    thu_muc_output
)