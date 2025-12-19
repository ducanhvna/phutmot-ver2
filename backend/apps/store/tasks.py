import logging
import hashlib
import uuid
import os
from typing import Optional
import psycopg2
import requests
from celery import shared_task
from decimal import Decimal

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


# =====================
# HARD-CODED CONFIG (special file)
# NOTE: per your request, this file must NOT read environment variables.
# =====================

REDIS_URL = "redis://redis:6379/0"

PAYMENT_DB = {
    "host": "118.70.146.150",
    "port": 5432,
    "dbname": "EmailTCKT",
    "user": "postgres",
    "password": "admin",
}

logger = logging.getLogger(__name__)

PAYMENT_CONFIRM_URL = "http://118.70.146.150:8869/api/public/Thanh_toan"


def _redis_client():
    if not redis:
        return None
    try:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None


def _poll_lock_key(trans_desc: str) -> str:
    digest = hashlib.sha256(trans_desc.encode("utf-8", errors="ignore")).hexdigest()
    return f"payment_poll:lock:{digest}"


_REDIS_RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
else
  return 0
end
"""


LOCK_TTL_SECONDS = 1800

# Polling cadence: reduce connection churn to Postgres.
# Total wait window is roughly POLL_INTERVAL_SECONDS * POLL_MAX_RETRIES.
POLL_INTERVAL_SECONDS = 10
POLL_MAX_RETRIES = 180


# Keep a single Postgres connection per Celery worker process to avoid
# reconnect storms when tasks retry frequently.
_PG_CONN = None
_PG_CONN_PID = None


def _pg_conn():
    global _PG_CONN, _PG_CONN_PID
    pid = os.getpid()

    if _PG_CONN is not None and _PG_CONN_PID == pid:
        try:
            if getattr(_PG_CONN, "closed", 1) == 0:
                return _PG_CONN
        except Exception:
            pass

    # Connection is missing/stale or after fork.
    try:
        if _PG_CONN is not None and getattr(_PG_CONN, "closed", 1) == 0:
            _PG_CONN.close()
    except Exception:
        pass

    _PG_CONN_PID = pid
    _PG_CONN = psycopg2.connect(
        **PAYMENT_DB,
        connect_timeout=5,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )
    return _PG_CONN


def _pg_reset_conn():
    global _PG_CONN
    try:
        if _PG_CONN is not None and getattr(_PG_CONN, "closed", 1) == 0:
            _PG_CONN.close()
    except Exception:
        pass
    _PG_CONN = None


def try_enqueue_poll_payment(id_don: str, trans_desc: str, loai: int = 1, ttl_seconds: int = LOCK_TTL_SECONDS) -> bool:

    if not id_don or not trans_desc:
        return False

    client = _redis_client()
    if not client:
        # Can't lock -> fall back to old behavior (enqueue).
        poll_payment_by_last_id_and_confirm.delay(id_don=str(id_don), trans_desc=str(trans_desc), loai=int(loai))
        return True

    key = _poll_lock_key(trans_desc)
    token = uuid.uuid4().hex
    try:
        acquired = client.set(key, token, nx=True, ex=int(ttl_seconds))
    except Exception:
        acquired = False

    if not acquired:
        return False

    poll_payment_by_last_id_and_confirm.delay(
        id_don=str(id_don),
        trans_desc=str(trans_desc),
        loai=int(loai),
        lock_token=token,
    )
    return True


def _json_number(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _pg_fetchone(conn, sql: str, params: tuple):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()

@shared_task(bind=True)
def poll_payment_by_last_id_and_confirm(self, id_don: str, trans_desc: str, loai: int = 1, lock_token: Optional[str] = None):
    """Poll Postgres webhook tables for a transaction description and confirm payment.

        Flow:
        - Postgres:
            - SELECT last_id FROM last_check_thanh_toan WHERE trans_desc = trans_desc
            - SELECT id, amount FROM webhook_transactions WHERE trans_desc = trans_desc ORDER BY id DESC LIMIT 1
            - Compare last_id with id
            - If new -> call PAYMENT_CONFIRM_URL (api/public/Thanh_toan)
            - Upsert last_check_thanh_toan (trans_desc, last_id)

        Note:
        - This task intentionally does NOT query SQL Server. It only polls webhook data and triggers the payment-confirm API.
        - The payload uses `amount` from `webhook_transactions` as `so_tien`.
    """

    if not id_don or not trans_desc:
        raise ValueError("id_don and trans_desc are required")

    # Ensure only the lock owner executes the polling logic.
    if lock_token:
        client = _redis_client()
        if client:
            key = _poll_lock_key(trans_desc)
            try:
                current = client.get(key)
            except Exception:
                current = None

            if current != lock_token:
                return {"skipped": True, "reason": "lock_not_owned", "trans_desc": trans_desc}

    try:
        conn = _pg_conn()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5, max_retries=360)

    try:
        last_row = _pg_fetchone(
            conn,
            "SELECT last_id FROM last_check_thanh_toan WHERE trans_desc = %s LIMIT 1",
            (trans_desc,),
        )
        last_id = last_row[0] if last_row else None

        max_row = _pg_fetchone(
            conn,
            "SELECT id, amount FROM webhook_transactions WHERE trans_desc = %s ORDER BY id DESC LIMIT 1",
            (trans_desc,),
        )
        max_id = max_row[0] if max_row else None
        amount = max_row[1] if max_row else None

        logger.info("poll_payment_by_last_id_and_confirm: last_id=%s max_id=%s trans_desc=%s", last_id, max_id, trans_desc)
    except Exception as exc:
        # Reset cached connection on DB errors.
        _pg_reset_conn()
        raise self.retry(exc=exc, countdown=5, max_retries=360)

    if not max_id:
        # Chưa có tiền về -> đợi
        if lock_token:
            client = _redis_client()
            if client:
                try:
                    client.expire(_poll_lock_key(trans_desc), LOCK_TTL_SECONDS)
                except Exception:
                    pass
        raise self.retry(countdown=POLL_INTERVAL_SECONDS, max_retries=POLL_MAX_RETRIES)

    # Determine if this is a new transaction (or first-seen)
    should_confirm = False
    if last_id is None:
        should_confirm = True
    else:
        try:
            should_confirm = int(last_id) < int(max_id)
        except Exception:
            # If parsing fails, be conservative and confirm once
            should_confirm = True

    if not should_confirm:
        # last_id == max_id -> chưa có giao dịch mới
        if lock_token:
            client = _redis_client()
            if client:
                try:
                    client.expire(_poll_lock_key(trans_desc), LOCK_TTL_SECONDS)
                except Exception:
                    pass
        raise self.retry(countdown=POLL_INTERVAL_SECONDS, max_retries=POLL_MAX_RETRIES)

    payload = {
        "ma_hoa_don": int(id_don) if str(id_don).isdigit() else id_don,
        "so_tien": _json_number(amount),
        "loai": loai
    }

    try:
        # Use `json=...` so requests sets Content-Type: application/json and serializes properly.
        resp = requests.post(
            PAYMENT_CONFIRM_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        print("Payment confirm response:", payload,  resp.status_code, resp.text)
        if not resp.ok:
            raise Exception(f"Payment confirm failed, dương thái: {payload}{resp.status_code} {resp.text}")
    except Exception as exc:
        logger.warning("Payment confirm call failed (no retry): trans_desc=%s id_don=%s error=%s", trans_desc, id_don, exc)

        # Do NOT retry on confirm failures (per requirement). Release lock so future flows can re-enqueue.
        if lock_token:
            client = _redis_client()
            if client:
                try:
                    client.eval(_REDIS_RELEASE_LUA, 1, _poll_lock_key(trans_desc), lock_token)
                except Exception:
                    pass

        return {
            "paid": False,
            "id_don": id_don,
            "so_tien": _json_number(amount),
            "trans_desc": trans_desc,
            "max_id": max_id,
            "amount": amount,
            "error": str(exc),
        }

    # Upsert last_check_thanh_toan
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE last_check_thanh_toan SET last_id = %s WHERE trans_desc = %s",
                (max_id, trans_desc),
            )
            updated = cur.rowcount
            if updated == 0:
                cur.execute(
                    "INSERT INTO last_check_thanh_toan (trans_desc, last_id) VALUES (%s, %s)",
                    (trans_desc, max_id),
                )
        conn.commit()
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        # Reset cached connection on write errors.
        _pg_reset_conn()
        raise self.retry(exc=exc, countdown=5, max_retries=360)
    finally:
        # Intentionally keep the cached connection open for reuse.
        pass

    # Release lock after successful confirm.
    if lock_token:
        client = _redis_client()
        if client:
            try:
                client.eval(_REDIS_RELEASE_LUA, 1, _poll_lock_key(trans_desc), lock_token)
            except Exception:
                pass

    return {
        "paid": True,
        "id_don": id_don,
        "so_tien": _json_number(amount),
        "trans_desc": trans_desc,
        "max_id": max_id,
        "amount": amount,
    }


# Backwards-compatible alias (some older code imported this symbol).
@shared_task(bind=True, name="apps.store.tasks.poll_payment_and_confirm")
def poll_payment_and_confirm(self, id_don: str, trans_desc: str, loai: int = 1, lock_token: Optional[str] = None):
    return poll_payment_by_last_id_and_confirm(
        self,
        id_don=id_don,
        trans_desc=trans_desc,
        loai=loai,
        lock_token=lock_token,
    )
