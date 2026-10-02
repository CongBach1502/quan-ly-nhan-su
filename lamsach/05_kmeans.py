from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

thu_muc = Path(__file__).parent
thu_muc_output = thu_muc / "output"
thu_muc_phan_tich = thu_muc_output / "phan_tich"

file_input = thu_muc_phan_tich / "cham_cong_theo_nhan_vien.csv"

file_ket_qua = thu_muc_output / "kmeans_ket_qua.csv"
file_thong_ke = thu_muc_output / "kmeans_thong_ke_nhom.csv"


# ============================================================
# 2. ĐỌC DỮ LIỆU
# ============================================================

print("=" * 70)
print("K-MEANS CLUSTERING NHÂN VIÊN")
print("=" * 70)

print("\nĐọc dữ liệu:")
print(file_input)

df = pd.read_csv(file_input, encoding="utf-8-sig")

print(f"Số nhân viên: {len(df)}")
print("\nCác cột dữ liệu:")
print(df.columns.tolist())


# ============================================================
# 3. CHỌN CÁC BIẾN ĐỂ PHÂN NHÓM
# ============================================================

cot_kmeans = [
    "so_ngay_cham_cong",
    "so_luot_di_muon",
    "tong_phut_di_muon",
    "gio_tb_moi_luot"
]

print("\nCác biến dùng cho K-Means:")
for cot in cot_kmeans:
    print("-", cot)


# Kiểm tra cột
cot_thieu = [cot for cot in cot_kmeans if cot not in df.columns]

if cot_thieu:
    print("\n❌ THIẾU CỘT:")
    for cot in cot_thieu:
        print("-", cot)

    print("\nHãy kiểm tra lại file cham_cong_theo_nhan_vien.csv")
    raise SystemExit


# ============================================================
# 4. CHUẨN BỊ DỮ LIỆU
# ============================================================

X = df[cot_kmeans].copy()

# Chuyển sang số
for cot in cot_kmeans:
    X[cot] = pd.to_numeric(X[cot], errors="coerce")

# Kiểm tra missing
print("\nSố giá trị thiếu:")
print(X.isna().sum())

# Thay missing bằng median của từng cột
for cot in cot_kmeans:
    X[cot] = X[cot].fillna(X[cot].median())


# ============================================================
# 5. CHUẨN HÓA DỮ LIỆU
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("\nĐã chuẩn hóa dữ liệu bằng StandardScaler.")


# ============================================================
# 6. K-MEANS
# ============================================================

so_nhom = 3

kmeans = KMeans(
    n_clusters=so_nhom,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(X_scaled)


# ============================================================
# 7. THỐNG KÊ ĐẶC ĐIỂM TỪNG NHÓM
# ============================================================

thong_ke = df.groupby("cluster")[cot_kmeans].mean().reset_index()

so_luong = (
    df["cluster"]
    .value_counts()
    .sort_index()
    .reset_index()
)

so_luong.columns = ["cluster", "so_nhan_vien"]

thong_ke = thong_ke.merge(
    so_luong,
    on="cluster",
    how="left"
)

# Đưa số nhân viên lên trước
cot_thong_ke = [
    "cluster",
    "so_nhan_vien",
    "so_ngay_cham_cong",
    "so_luot_di_muon",
    "tong_phut_di_muon",
    "gio_tb_moi_luot"
]

thong_ke = thong_ke[cot_thong_ke]


# ============================================================
# 8. IN KẾT QUẢ
# ============================================================

print("\n" + "=" * 70)
print("KẾT QUẢ PHÂN NHÓM")
print("=" * 70)

print(thong_ke.to_string(index=False))


print("\n" + "=" * 70)
print("SỐ LƯỢNG NHÂN VIÊN THEO NHÓM")
print("=" * 70)

print(
    df["cluster"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# 9. XUẤT KẾT QUẢ
# ============================================================

df.to_csv(
    file_ket_qua,
    index=False,
    encoding="utf-8-sig"
)

thong_ke.to_csv(
    file_thong_ke,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("ĐÃ XUẤT KẾT QUẢ")
print("=" * 70)

print("File 1:")
print(file_ket_qua)

print("\nFile 2:")
print(file_thong_ke)

print("\nHoàn thành K-Means.")