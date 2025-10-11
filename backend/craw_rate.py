import requests
import xmlrpc.client
import time

# Trì hoãn 20 giây trước khi gọi API
# print("⏳ Đang chờ 40 giây trước khi gọi API...")
# time.sleep(40)
# Cấu hình Odoo
ODOO_URL = 'https://solienlacdientu.info'
ODOO_DB = 'goldsun'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

# Kết nối Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Gọi API tỷ giá vàng
api_url = 'https://sjc.com.vn/GoldPrice/Services/PriceService.ashx'
# response = requests.get(api_url)
# data = response.json()

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# # Delay 20 giây trước khi gọi API
# print("⏳ Đang chờ 20 giây trước khi gọi API...")
# time.sleep(20)

# Cấu hình retry và headers
session = requests.Session()
retry = Retry(
    total=3,                # Thử lại tối đa 3 lần
    backoff_factor=2,       # Mỗi lần retry cách nhau 2s, 4s, 8s
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json'
}

try:
    response = session.get(api_url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    print("✅ Đã lấy dữ liệu thành công.", data)
except requests.exceptions.RequestException as e:
    print(f"❌ Lỗi khi gọi API: {e}")


from datetime import date

today = date.today().isoformat()

# Lấy danh sách full_name đã có để kiểm tra trùng
existing_currencies = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'res.currency', 'search_read',
    [[('full_name', '!=', False)]],
    {'fields': ['id', 'full_name', 'name']})

existing_full_names = {c['full_name']: c['id'] for c in existing_currencies}
existing_codes = {c['name'] for c in existing_currencies}

# Hàm tạo mã tiền tệ mới
def generate_currency_code(existing_codes):
    i = 1
    while True:
        code = f"S{i:02d}"
        if code not in existing_codes:
            return code
        i += 1

# Xử lý từng dòng dữ liệu
for item in data['data']:
    full_name = f"{item['TypeName']} - {item['BranchName']}"
    buy_value = item['BuyValue']

    # Kiểm tra trùng theo full_name
    if full_name in existing_full_names:
        currency_id = existing_full_names[full_name]
    else:
        currency_code = generate_currency_code(existing_codes)
        currency_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.currency', 'create',
            [{
                'name': currency_code,
                'full_name': full_name,
                'symbol': 'SJC',
                'currency_unit_label': 'lượng',
                'currency_subunit_label': 'chỉ',
                'decimal_places': 0,
                'active': True
            }])
        print(f"🆕 Tạo mới loại vàng: {full_name} với mã {currency_code}")
        existing_full_names[full_name] = currency_id
        existing_codes.add(currency_code)

    # Kiểm tra tỷ giá theo ngày
    rate_domain = [('currency_id', '=', currency_id), ('name', '=', today)]
    rate_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'res.currency.rate', 'search_read',
        [rate_domain], {'fields': ['id', 'rate']})

    if rate_ids:
        rate_id = rate_ids[0]['id']
        old_rate = rate_ids[0]['rate']
        if old_rate != buy_value:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'res.currency.rate', 'write',
                [[rate_id], {'rate': buy_value}])
            print(f"✅ Cập nhật tỷ giá: {full_name}")
        else:
            print(f"➖ Không thay đổi tỷ giá: {full_name}")
    else:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'res.currency.rate', 'create',
            [{
                'currency_id': currency_id,
                'name': today,
                'rate': buy_value
            }])
        print(f"🆕 Tạo tỷ giá mới: {full_name}")
