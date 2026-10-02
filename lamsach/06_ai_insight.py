import pandas as pd
from pathlib import Path

# ============================================================
# 06 - AI INSIGHT TỪ KẾT QUẢ K-MEANS
# ============================================================

thu_muc = Path(__file__).parent

file_ket_qua = thu_muc / "output" / "kmeans_ket_qua.csv"
file_thong_ke = thu_muc / "output" / "kmeans_thong_ke_nhom.csv"

file_output = thu_muc / "output" / "ai_insight.csv"


print("=" * 70)
print("AI INSIGHT - PHÂN TÍCH NHÓM NHÂN VIÊN")
print("=" * 70)


# ============================================================
# 1. ĐỌC DỮ LIỆU
# ============================================================

print("\nĐọc dữ liệu K-Means...")

df = pd.read_csv(file_ket_qua, encoding="utf-8-sig")
df_thong_ke = pd.read_csv(file_thong_ke, encoding="utf-8-sig")

print(f"Số nhân viên: {len(df)}")
print(f"Số nhóm: {df['cluster'].nunique()}")


# ============================================================
# 2. PHÂN TÍCH ĐẶC ĐIỂM CÁC NHÓM
# ============================================================

print("\n" + "=" * 70)
print("PHÂN TÍCH CÁC NHÓM")
print("=" * 70)

# Tìm nhóm có giá trị cao/thấp
nhom_di_muon_nhieu = df_thong_ke.loc[
    df_thong_ke["tong_phut_di_muon"].idxmax(), "cluster"
]

nhom_di_muon_it = df_thong_ke.loc[
    df_thong_ke["tong_phut_di_muon"].idxmin(), "cluster"
]

nhom_luot_di_muon_nhieu = df_thong_ke.loc[
    df_thong_ke["so_luot_di_muon"].idxmax(), "cluster"
]

nhom_luot_di_muon_it = df_thong_ke.loc[
    df_thong_ke["so_luot_di_muon"].idxmin(), "cluster"
]


# ============================================================
# 3. TẠO INSIGHT CHO TỪNG NHÓM
# ============================================================

ket_qua = []

for _, row in df_thong_ke.iterrows():

    cluster = int(row["cluster"])

    so_nv = int(row["so_nhan_vien"])
    so_ngay = row["so_ngay_cham_cong"]
    so_luot_muon = row["so_luot_di_muon"]
    tong_phut_muon = row["tong_phut_di_muon"]
    gio_tb = row["gio_tb_moi_luot"]

    # --------------------------------------------------------
    # Xác định đặc điểm nhóm
    # --------------------------------------------------------

    if cluster == nhom_di_muon_nhieu:
        muc_do_di_muon = "cao"
    elif cluster == nhom_di_muon_it:
        muc_do_di_muon = "thấp"
    else:
        muc_do_di_muon = "trung bình"

    if cluster == nhom_luot_di_muon_nhieu:
        tan_suat_di_muon = "cao"
    elif cluster == nhom_luot_di_muon_it:
        tan_suat_di_muon = "thấp"
    else:
        tan_suat_di_muon = "trung bình"

    # --------------------------------------------------------
    # Sinh nhận xét
    # --------------------------------------------------------

    if cluster == nhom_di_muon_nhieu:

        ten_nhom = "Nhóm có xu hướng đi muộn cao"

        nhan_xet = (
            f"Nhóm này gồm {so_nv} nhân viên. "
            f"Trung bình mỗi nhân viên có {so_luot_muon:.2f} lượt đi muộn, "
            f"tổng thời gian đi muộn trung bình {tong_phut_muon:.2f} phút. "
            f"Đây là nhóm có tổng thời gian đi muộn cao nhất trong các nhóm."
        )

        goi_y = (
            "Có thể theo dõi riêng tình trạng đi muộn, "
            "phân tích nguyên nhân và xem xét các biện pháp cải thiện thời gian đi làm."
        )

    elif cluster == nhom_di_muon_it:

        ten_nhom = "Nhóm có xu hướng đi muộn thấp"

        nhan_xet = (
            f"Nhóm này gồm {so_nv} nhân viên. "
            f"Trung bình mỗi nhân viên có {so_luot_muon:.2f} lượt đi muộn, "
            f"tổng thời gian đi muộn trung bình {tong_phut_muon:.2f} phút. "
            f"Đây là nhóm có tổng thời gian đi muộn thấp nhất trong các nhóm."
        )

        goi_y = (
            "Có thể sử dụng nhóm này làm nhóm tham chiếu "
            "khi phân tích tình trạng đi muộn của nhân viên."
        )

    else:

        ten_nhom = "Nhóm có mức đi muộn trung gian"

        nhan_xet = (
            f"Nhóm này gồm {so_nv} nhân viên. "
            f"Trung bình mỗi nhân viên có {so_luot_muon:.2f} lượt đi muộn, "
            f"tổng thời gian đi muộn trung bình {tong_phut_muon:.2f} phút. "
            f"Mức độ đi muộn nằm giữa các nhóm còn lại."
        )

        goi_y = (
            "Nên tiếp tục theo dõi dữ liệu chấm công "
            "để xác định xu hướng thay đổi của nhóm."
        )

    # --------------------------------------------------------
    # Lưu kết quả
    # --------------------------------------------------------

    ket_qua.append({
        "cluster": cluster,
        "ten_nhom": ten_nhom,
        "so_nhan_vien": so_nv,
        "so_ngay_cham_cong_tb": round(so_ngay, 2),
        "so_luot_di_muon_tb": round(so_luot_muon, 2),
        "tong_phut_di_muon_tb": round(tong_phut_muon, 2),
        "gio_tb_moi_luot": round(gio_tb, 3),
        "muc_do_di_muon": muc_do_di_muon,
        "tan_suat_di_muon": tan_suat_di_muon,
        "nhan_xet_ai": nhan_xet,
        "goi_y_ai": goi_y
    })


# ============================================================
# 4. TẠO DATAFRAME
# ============================================================

df_ai = pd.DataFrame(ket_qua)


# ============================================================
# 5. HIỂN THỊ KẾT QUẢ
# ============================================================

print("\n" + "=" * 70)
print("KẾT QUẢ AI INSIGHT")
print("=" * 70)

for _, row in df_ai.iterrows():

    print(f"\n--- CLUSTER {row['cluster']} ---")
    print(f"Tên nhóm: {row['ten_nhom']}")
    print(f"Số nhân viên: {row['so_nhan_vien']}")
    print(f"Mức độ đi muộn: {row['muc_do_di_muon']}")
    print(f"Tần suất đi muộn: {row['tan_suat_di_muon']}")
    print(f"Nhận xét: {row['nhan_xet_ai']}")
    print(f"Gợi ý: {row['goi_y_ai']}")


# ============================================================
# 6. XUẤT FILE
# ============================================================

df_ai.to_csv(
    file_output,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("ĐÃ XUẤT KẾT QUẢ AI")
print("=" * 70)

print(f"\nFile:")
print(file_output)

print("\nHoàn thành AI Insight.")