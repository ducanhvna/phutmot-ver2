# yourapp/tasks.py
from celery import shared_task
import xmlrpc.client
import time
import requests
import logging
logger = logging.getLogger(__name__)

# @shared_task
# def collect_data():
#     logger.info("Thu thập dữ liệu mỗi phút...")
#     ...
#     logger.info("✅ Đã lấy dữ liệu thành công.")
#     ...
#     logger.error(f"❌ Lỗi khi gọi API: {e}")

@shared_task
def collect_data():
    # print("Thu thập dữ liệu mỗi phút...")
    logger.info("Thu thập dữ liệu mỗi phút...")
    # Trì hoãn 20 giây trước khi gọi API
    # print("⏳ Đang chờ 40 giây trước khi gọi API...")
    # time.sleep(40)
    # Cấu hình Odoo
    # ODOO_URL = 'https://solienlacdientu.info'
    # ODOO_DB = 'goldsun'
    # ODOO_USERNAME = 'admin'
    # ODOO_PASSWORD = 'admin'

    # # Kết nối Odoo
    # common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    # uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    # models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # # Gọi API tỷ giá vàng
    # api_url = 'https://sjc.com.vn/GoldPrice/Services/PriceService.ashx'
    # # response = requests.get(api_url)
    # # data = response.json()

    # from requests.adapters import HTTPAdapter
    # from urllib3.util.retry import Retry

    # # # Delay 20 giây trước khi gọi API
    # # print("⏳ Đang chờ 20 giây trước khi gọi API...")
    # # time.sleep(20)

    # # Cấu hình retry và headers
    # session = requests.Session()
    # retry = Retry(
    #     total=3,                # Thử lại tối đa 3 lần
    #     backoff_factor=2,       # Mỗi lần retry cách nhau 2s, 4s, 8s
    #     status_forcelist=[500, 502, 503, 504],
    #     raise_on_status=False
    # )
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)

    # headers = {
    #     'User-Agent': 'Mozilla/5.0',
    #     'Accept': 'application/json'
    # }

    # try:
    #     response = session.get(api_url, headers=headers, timeout=10)
    #     response.raise_for_status()
    #     data = response.json()
    #     logger.error("✅ Đã lấy dữ liệu thành công.")
    # except requests.exceptions.RequestException as e:
    #     logger.error(f"❌ Lỗi khi gọi API: {e}")

