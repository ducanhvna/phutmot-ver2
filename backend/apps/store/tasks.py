import os
import psycopg2
import requests
from celery import shared_task

PAYMENT_DB = {
    "host": os.getenv("PAYMENT_DB_HOST", "118.70.146.150"),
    "port": int(os.getenv("PAYMENT_DB_PORT", "5432")),
    "dbname": os.getenv("PAYMENT_DB_NAME", "EmailTCKT"),
    "user": os.getenv("PAYMENT_DB_USER", "postgres"),
    "password": os.getenv("PAYMENT_DB_PASSWORD", "admin"),
}

PAYMENT_CONFIRM_URL = os.getenv(
    "PAYMENT_CONFIRM_URL",
    "http://192.168.0.223:8869/api/public/Thanh_toan",
)

SRC_ACCOUNT_NUMBER = os.getenv("PAYMENT_SRC_ACCOUNT", "85868855111")
TRANS_TYPE = "C"


@shared_task(bind=True)
def poll_payment_and_confirm(self, id_don: str):
    sql = (
        "SELECT amount FROM webhook_transactions "
        "WHERE src_account_number = %s AND trans_type = %s AND trans_desc = %s "
        "ORDER BY created_at DESC LIMIT 1"
    )
    params = (SRC_ACCOUNT_NUMBER, TRANS_TYPE, f"{id_don} - APPSALE")

    try:
        conn = psycopg2.connect(**PAYMENT_DB)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
        finally:
            conn.close()
    except Exception as exc:
        # connection/query issue -> retry with 5s backoff, up to ~30 minutes
        raise self.retry(exc=exc, countdown=5, max_retries=360)

    if not row:
        # Not found yet -> retry every 5s, stop after ~30 minutes
        raise self.retry(countdown=3, max_retries=360)

    amount = row[0]
    ma_hoa_don = id_don  # ma_hoa_don chính là id_don
    payload = {"ma_hoa_don": ma_hoa_don, "so_tien": amount, "loai": 1}

    try:
        resp = requests.post(PAYMENT_CONFIRM_URL, json=payload, timeout=15)
        if not resp.ok:
            raise Exception(f"Payment confirm failed: {resp.status_code} {resp.text}")
    except Exception as exc:
        # allow retries for transient payment errors, but still cap at 30 minutes total
        raise self.retry(exc=exc, countdown=5, max_retries=360)

    return {"paid": True, "amount": amount, "ma_hoa_don": ma_hoa_don}
