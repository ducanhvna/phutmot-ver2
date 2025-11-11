import pandas as pd

# Load dữ liệu từ các bảng
df_dmH = pd.read_parquet('data/Product/DmH.parquet')
df_dmQTTG = pd.read_parquet('data/Product/DmQTTG.parquet')
df_dmVBTG = pd.read_parquet('data/Product/DmVbMM.parquet')

# Kiểm tra tên cột trong bảng tỷ giá để tránh lỗi KeyError
print("Các cột trong df_dmVBTG:", df_dmVBTG.columns.tolist())

# Hàm lấy công thức theo mã sản phẩm
def get_formula(ma_hang):
    row = df_dmH[df_dmH['Ma_Hang'] == ma_hang].iloc[0]
    id_qttg = row['ID_QTTG']
    qttg = df_dmQTTG[df_dmQTTG['ID'] == id_qttg].iloc[0]
    return qttg['Ma_QTTG'], qttg

# Hàm tính giá đơn giản cho loại GB-24VD
def tinh_gia(ma_hang):
    row = df_dmH[df_dmH['Ma_Hang'] == ma_hang].iloc[0]
    ma_qttg, qttg = get_formula(ma_hang)

    # Lấy các biến cần thiết
    TL_KLoai = row['T_Luong']
    Tien_C_B = row['Gia_Ban5']
    Tien_Da_B = row['Gia_Ban1']

    # Kiểm tra tên cột tỷ giá
    ty_gia_col = next((c for c in df_dmVBTG.columns if 'TyGia_Ban' in c or 'Ty_Gia_Ban' in c), None)
    if not ty_gia_col:
        raise KeyError("Không tìm thấy cột tỷ giá bán trong df_dmVBTG")

    TyGia_Ban = df_dmVBTG[df_dmVBTG['ID'] == row['ID_VBTG']].iloc[0][ty_gia_col]

    # Áp dụng công thức cho loại GB-24VD
    if ma_qttg == 'GB-24VD':
        return TL_KLoai * TyGia_Ban + Tien_C_B + Tien_Da_B
    else:
        return None  # hoặc mở rộng cho các loại khác

# Lấy 10 mã sản phẩm đầu tiên và tính giá
ma_hangs = df_dmH['Ma_Hang'].head(10).tolist()
for ma in ma_hangs:
    try:
        gia = tinh_gia(ma)
        print(f'Mã hàng: {ma} → Giá bán: {gia}')
    except Exception as e:
        print(f'Lỗi khi xử lý mã hàng {ma}: {e}')

