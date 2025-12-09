# file: data_loader.py
import pandas as pd

df_dmH = pd.read_parquet('data/Product/DmH.parquet')
df_dmQTTG = pd.read_parquet('data/Product/DmQTTG.parquet')
df_dmVBTG = pd.read_parquet('data/Product/DmVbMM.parquet')

# Nếu bạn cần gửi payload (JSON, form...), ví dụ:
CLIENT_CERT_PATH = "data/Product/client_cert.pem"
CLIENT_KEY_PATH = "data/Product/client_key.pem"
CA_CERT_PATH = False  # Nếu cần xác thực server
# Đường dẫn tới file chứng chỉ và key
cert = (CLIENT_CERT_PATH, CLIENT_KEY_PATH)