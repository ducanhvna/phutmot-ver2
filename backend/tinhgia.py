# file: data_loader.py
import pandas as pd

df_dmH = pd.read_parquet('data/Product/DmH.parquet')
df_dmQTTG = pd.read_parquet('data/Product/DmQTTG.parquet')
df_dmVBTG = pd.read_parquet('data/Product/DmVbMM.parquet')

import requests

url = "https://14.224.192.52:9999/api/v1/calculate-price"

# Nếu bạn cần gửi payload (JSON, form...), ví dụ:
CLIENT_CERT_PATH = "data/Product/client_cert.pem"
CLIENT_KEY_PATH = "data/Product/client_key.pem"
CA_CERT_PATH = "data/Product/ca_cert.pem"  # Nếu cần xác thực server
# Đường dẫn tới file chứng chỉ và key
cert = (CLIENT_CERT_PATH, CLIENT_KEY_PATH)
# Nếu server dùng self-signed cert, bạn có thể cần ca-cert.pem hoặc tắt verify (không khuyến nghị cho production)
response = requests.post(
    url,
    json={"ma_hang": "KGB1C10022001"},
    cert=cert,
    verify= CA_CERT_PATH # hoặc verify=False nếu chỉ test
)

print(response.status_code)
tygia = response.json()
print(tygia)

# Giả sử tỷ giá USD được lấy từ bảng DmTt
# TyGia_TT =  df_dmH['Ty_Gia'].mean()  # hoặc lấy từ bảng khác nếu có

def tinh_gia_ban(row):
    # Lấy dữ liệu liên quan từ các bảng
    qttg_row = df_dmQTTG[df_dmQTTG['ID'] == row['ID_QTTG']].squeeze()
    vbtg_row = df_dmVBTG[df_dmVBTG['ID'] == row['ID_VBTG']].squeeze()

    # Các biến cần thiết
    TL_KLoai = row['T_Luong']
    TL_Da_C = row['The_Tich']
    T_LuongTT = row['T_LuongTT']
    Tien_Da_B = row['Gia_Ban1']
    Tien_Da_BN = row['Gia_Ban2']
    Tien_C_B = row['Gia_Ban5']
    Tien_C_BN = row['Gia_Ban6']
    Tien_Da_M = row['Gia_Ban3']
    Tien_Da_MN = row['Gia_Ban4']
    Tien_C_M = row['Gia_Ban7']
    Tien_C_MN = row['Gia_Ban8']
    Gia_B_TG = row['Gia_Ban9']
    Gia_B_TGN = row['Gia_Ban10']
    Gia_M_TG = row['Gia_Ban11']
    Gia_M_TGN = row['Gia_Ban12']
    TyGia_Ban = tygia['ty_gia_vang_ban_niem_yet']
    TG_Mua_NY = tygia['ty_gia_vang_mua_niem_yet']
    Tygia_Mua = tygia['ty_gia_vang_mua_niem_yet']
    TyGia_TT = tygia['ty_gia_tien_te_ban_niem_yet']
    TyGiaV_TG = row['Sl_Min']
    TyGia_MuaN = row['Luu_Kho']
    Hao_G_Cong = row['Tyle_GBL']
    Ma_QTTG = qttg_row['Ma_QTTG']
    He_So1 = qttg_row['He_So1']
    He_So2 = qttg_row['He_So2']
    He_So3 = qttg_row['He_So3']
    He_So4 = qttg_row['He_So4']
    He_So5 = qttg_row['He_So5']
    He_So6 = qttg_row['He_So6']

    Tong_TL = TL_KLoai + TL_Da_C + T_LuongTT

    # Logic tính giá theo Ma_QTTG
    if Ma_QTTG in ['GB-10K-ORD', 'GB-14K-ORD', 'GB-18K-ORD']:
        result = He_So1 * He_So2 * TyGia_Ban * TL_KLoai + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-24VD':
        result = TL_KLoai * TyGia_Ban + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-BA-TG':
        result = Gia_B_TG + Tien_C_B + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-BAC':
        result = TL_KLoai * TyGia_Ban + Tien_C_B + Tien_Da_B
    elif Ma_QTTG.startswith('GB-CN-CC') or Ma_QTTG == 'GB-CN-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2) + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-CN-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'GB-KGB':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG.startswith('GB-NC-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-NC-CC') or Ma_QTTG == 'GB-NC-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2) + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG.startswith('GB-NCKC-1'):
        result = He_So1 * (TL_KLoai * TyGiaV_TG + Tien_C_M + Tien_C_MN * TyGia_MuaN + Tien_Da_M + Tien_Da_MN * TyGia_MuaN)
    elif Ma_QTTG.startswith('GB-NH-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-PH-1'):
        result = TyGiaV_TG * Tong_TL * He_So1
    elif Ma_QTTG == 'GB-PH-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'GB-PT':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG.startswith('GB-PY-1'):
        result = Tong_TL * (TyGiaV_TG + He_So1)
    elif Ma_QTTG.startswith('GB-PY-CC') or Ma_QTTG == 'GB-PY-PT':
        result = Tong_TL * (TyGia_Ban + He_So1 * He_So2)
    elif Ma_QTTG == 'GB-SJC':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG == 'GB-TK-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT + Tien_Da_B + Tien_Da_BN * TyGia_TT
    elif Ma_QTTG == 'GB-VRTL':
        result = TL_KLoai * TyGia_Ban
    elif Ma_QTTG.startswith('GB-VT-1'):
        result = He_So1 * (TL_KLoai * He_So2 * TyGiaV_TG + Tien_Da_M + (Tien_C_M + TL_KLoai * Hao_G_Cong * Tygia_Mua / He_So2)) + He_So4
    elif Ma_QTTG == 'GB-VT-TG':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'TRONGOI-GB':
        result = Gia_B_TG + Gia_B_TGN * TyGia_TT
    elif Ma_QTTG == 'TTXVV24K-GIABAN':
        result = TL_KLoai * TyGia_Ban
    else:
        result = 0

    return round(result, -3)

# Áp dụng hàm tính giá cho toàn bộ bảng
# Bước 4: Lọc các dòng có công thức khác nhau
# Merge các bảng để có đầy đủ thông tin
df_merged = df_dmH.merge(df_dmQTTG, left_on='ID_QTTG', right_on='ID', how='left') \
                  .merge(df_dmVBTG, left_on='ID_VBTG', right_on='ID', how='left', suffixes=('', '_VBTG'))

# Tạo cột Cong_Thuc_ID từ các cột đã có sau khi merge
cols_anh_huong = ['Ma_QTTG', 'He_So1', 'He_So2', 'He_So3', 'He_So4', 'He_So5', 'He_So6',
                  'Ty_Gia', 'Sl_Min', 'Luu_Kho', 'Tyle_GBL',
                  'Gia_Ban1', 'Gia_Ban2', 'Gia_Ban3', 'Gia_Ban4', 'Gia_Ban5', 'Gia_Ban6',
                  'Gia_Ban7', 'Gia_Ban8', 'Gia_Ban9', 'Gia_Ban10', 'Gia_Ban11', 'Gia_Ban12']

df_merged['Cong_Thuc_ID'] = df_merged[cols_anh_huong].astype(str).agg('-'.join, axis=1)
df_unique = df_merged.drop_duplicates(subset=['Cong_Thuc_ID'])

# Tính giá
# df_unique['Gia_Ban_TinhToan'] = df_unique.apply(tinh_gia_ban, axis=1)

# df_unique.to_excel('data/Product/DmH_with_calculated_price.xlsx', index=False)
