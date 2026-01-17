# syncodoo.py
import logging
import time
import functools
from typing import Any, List, Dict, Optional
import requests
from django.conf import settings
from apps.store.simple_api_warehouse import ApiWarehouse

_logger = logging.getLogger(__name__)

# -------------------------
# Simple retry decorator
# -------------------------
def simple_retry(attempts: int = 3, wait_seconds: int = 2, retry_exceptions: tuple = (Exception,)):
    """
    Simple retry decorator to replace tenacity for basic retry behavior.
    Usage: @simple_retry(attempts=3, wait_seconds=2, retry_exceptions=(OdooRPCError,))
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as exc:
                    last_exc = exc
                    _logger.warning("Attempt %s/%s failed with %s; retrying in %ss...", attempt, attempts, exc, wait_seconds)
                    if attempt < attempts:
                        time.sleep(wait_seconds)
                    else:
                        _logger.error("All %s attempts failed.", attempts)
                        raise
            raise last_exc
        return wrapper
    return decorator

# ============================================================
# Odoo RPC Client
# ============================================================
class OdooRPCError(Exception):
    """Base exception for Odoo RPC errors."""


class OdooAuthError(OdooRPCError):
    """Authentication or session error."""


class OdooClient:
    """
    Odoo JSON-RPC client for Odoo 18+ using /web/session/authenticate and
    /web/dataset/call_kw endpoints.
    """

    def __init__(self, base_url: str, db: str, username: str, password: str):
        base_url = base_url.strip().rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"
            _logger.warning("URL không có protocol, tự động thêm http://: %s", base_url)

        self.base_url = base_url
        self.db = db
        self.username = username
        self.password = password
        self.timeout = getattr(settings, "ODOO_TIMEOUT", 30)

        self.session = requests.Session()
        self._authenticated = False

        self.authenticate()

    # ---------------------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------------------
    def authenticate(self) -> None:
        url = f"{self.base_url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password,
            },
        }

        _logger.info("Authenticating to Odoo %s (db=%s)", self.base_url, self.db)
        resp = self.session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()
        if "error" in data:
            _logger.error("Odoo auth error: %s", data["error"])
            raise OdooAuthError(data["error"])

        self._authenticated = True
        _logger.info("Authenticated to Odoo successfully")

    # ---------------------------------------------------------------------
    # Low-level call (with simple_retry)
    # ---------------------------------------------------------------------
    @simple_retry(attempts=3, wait_seconds=2, retry_exceptions=(OdooRPCError,))
    def _call(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Call Odoo model method via JSON-RPC. Re-authenticates automatically
        when session expires.
        """
        if not self._authenticated:
            self.authenticate()

        url = f"{self.base_url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {},
            },
        }

        resp = self.session.post(url, json=payload, timeout=self.timeout)

        # Session expired or unauthorized
        if resp.status_code in (401, 403):
            _logger.warning("Odoo session expired (status %s), re-authenticating...", resp.status_code)
            self._authenticated = False
            self.authenticate()
            raise OdooRPCError("Session expired, retrying...")

        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            error = data["error"]
            # Try to extract useful info
            error_data = error.get("data", {})
            name = error_data.get("name")
            message = error_data.get("message") or error.get("message") or str(error)
            debug = error_data.get("debug", "")

            _logger.error("Odoo RPC error: %s", message)
            if debug:
                _logger.debug("Odoo debug: %s", debug)

            # Re-auth on session related errors
            if name in ("AccessError", "SessionExpiredException"):
                self._authenticated = False
                raise OdooRPCError(f"Odoo {name}: {message}")

            raise OdooRPCError(message)

        return data.get("result")

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def search(self, model: str, domain: List[Any], limit: int = 0) -> List[int]:
        kwargs = {"limit": limit} if limit else {}
        return self._call(model, "search", args=[domain], kwargs=kwargs)

    def read(self, model: str, ids: List[int], fields: List[str]) -> List[Dict]:
        return self._call(model, "read", args=[ids], kwargs={"fields": fields})

    def search_read(
        self,
        model: str,
        domain: List[Any],
        fields: List[str],
        limit: int = 0,
    ) -> List[Dict]:
        return self._call(model, "search_read", args=[domain], kwargs={"fields": fields, "limit": limit})

    def create(self, model: str, values: Dict[str, Any]) -> int:
        _logger.info("Creating %s with keys: %s", model, list(values.keys()))
        return self._call(model, "create", args=[values])

    def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        return self._call(model, "write", args=[ids, values])

    def unlink(self, model: str, ids: List[int]) -> bool:
        return self._call(model, "unlink", args=[ids])

    def call_method(self, model: str, method: str, ids: List[int], **kwargs) -> Any:
        return self._call(model, method, args=[ids], kwargs=kwargs)


# ============================================================
# External API Client
# ============================================================
class ApiClient:
    """
    Client để gọi API bên ngoài (ví dụ: hệ thống kho).
    """

    def __init__(self, base_url: str = settings.INTERNAL_API_BASE, timeout: int = getattr(settings, "API_TIMEOUT", 30)):
        self.base_url = (base_url or "").rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        _logger.info("Calling external API: %s", url)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # trong syncodoo.py, class ApiClient
    def get_product_warehouse_info(self, product_code: str, warehouse_code: str) -> ApiWarehouse:
        """
        Lấy thông tin hàng mã kho theo mã sản phẩm và mã kho.
        Trả về ApiWarehouse object bằng cách dùng ApiWarehouse.from_dict(...)
        """
        endpoint = f"/api/public/hang_ma_kho/{product_code}/{warehouse_code}"
        result = self._get(endpoint)
        warehouse_data = result.get("data", {}) or {}

        _logger.info("Product warehouse info for %s/%s: %s", product_code, warehouse_code, warehouse_data)

        # Sử dụng from_dict để tránh lỗi __init__(**kwargs)
        return ApiWarehouse.from_dict(warehouse_data)



# ============================================================
# ProductTemplate helper (thin wrapper using OdooClient)
# ============================================================
class ProductTemplate:
    def __init__(self, odoo: OdooClient):
        self.odoo = odoo

    def create_product(self, name: str, list_price: float, default_code: str,
                       uom_id: Optional[int] = None, uom_po_id: Optional[int] = None,
                       categ_id: Optional[int] = None) -> int:
        payload: Dict[str, Any] = {
            "name": name,
            "list_price": list_price,
            "default_code": default_code,
        }
        if uom_id is not None:
            payload["uom_id"] = uom_id
        if uom_po_id is not None:
            payload["uom_po_id"] = uom_po_id
        if categ_id is not None:
            payload["categ_id"] = categ_id

        return self.odoo.create("product.template", payload)

    def create_serial(self, product_id: int, serial_name: str) -> int:
        payload = {"name": serial_name, "product_id": product_id}
        return self.odoo.create("stock.lot", payload)


# ============================================================
# ProductSyncService: đồng bộ dữ liệu từ API về Odoo
# ============================================================
class ProductSyncService:
    def __init__(self, odoo_client: OdooClient, api_client: ApiClient):
        self.odoo = odoo_client
        self.api = api_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def sync_product_and_serial(self, code: str, warehouse_code: str) -> Dict[str, Optional[int]]:
        """
        Đồng bộ sản phẩm và serial từ API vào Odoo.

        - Nếu code.split('-') có 3 phần:
            sku = phần 1 + '-' + phần 2
            serial = full code
        - Ngược lại:
            sku = full code
            serial = None (không tạo)

        Hành vi bổ sung:
        - Luôn tìm serial trước. Nếu tìm thấy serial (stock.lot) thì
        hàm **ngay lập tức** trả về cả serial_id và product_id (nếu có).
        - Nếu không tìm thấy serial thì tiếp tục luồng bình thường: lấy dữ liệu từ API,
        đồng bộ product và tạo serial (nếu cần).

        Trả về dict: {"product_id": int | None, "serial_id": int | None}
        """
        # Nếu serial đã tồn tại trong Odoo -> trả về ngay
        parts = code.split("-")
        if len(parts) == 3:
            try:
                lot_ids = self.odoo.search("stock.lot", [("name", "=", code)], limit=1)
            except Exception as e:
                _logger.exception("Failed to search for serial %s: %s", code, e)
                lot_ids = []

            if lot_ids and len (lot_ids)>0:
                lot_id = lot_ids[0]
                # cố gắng đọc product_id từ lot
                try:
                    recs = self.odoo.read("stock.lot", [lot_id], ["product_id"])
                    if recs:
                        product_field = recs[0].get("product_id")
                        # product_field có thể là dạng (id, name) hoặc id
                        if isinstance(product_field, (list, tuple)) and product_field:
                            product_id = product_field[0]
                        else:
                            product_id = int(product_field) if product_field else None
                    else:
                        product_id = None
                    _logger.info("Found existing serial %s -> lot_id=%s, product_id=%s", code, lot_id, product_id)
                    return {"product_id": product_id, "lot_id": lot_id}
                except Exception as e:
                    _logger.exception("Failed to read stock.lot %s: %s", lot_id, e)
                    product_id = None

        # Nếu chưa có serial, tiếp tục luồng bình thường
        parts = code.split("-")
        if len(parts) == 3:
            sku = "-".join(parts[:2])
            serial_code = code
        else:
            sku = code
            serial_code = None

        _logger.info(
            "Sync request: code=%s, resolved sku=%s, serial=%s, warehouse=%s",
            code,
            sku,
            serial_code,
            warehouse_code,
        )

        # Lấy dữ liệu từ API (lưu ý dùng sku để lấy thông tin sản phẩm)
        product_data = self.api.get_product_warehouse_info(code, warehouse_code)

        # Đồng bộ product -> trả về product.product id (variant)
        product_id = self.sync_product(product_data)

        serial_id: Optional[int] = None
        if serial_code and product_id:
            # Tạo serial (stock.lot) liên kết với product.product
            try:
                serial_payload = {"name": serial_code, "product_id": product_id}
                serial_id = self.odoo.create("stock.lot", serial_payload)
                _logger.info(
                    "Created serial %s (id=%s) for product_variant %s",
                    serial_code,
                    serial_id,
                    product_id,
                )
            except Exception as e:
                _logger.exception(
                    "Failed to create serial %s for product %s: %s",
                    serial_code,
                    product_id,
                    e,
                )
                raise

        return {"product_id": product_id, "lot_id": serial_id}

    def sync_product(self, product: ApiWarehouse) -> Optional[int]:
        """
        Đồng bộ một ApiWarehouse object vào Odoo.
        Trả về product.product id (variant).
        """
        try:
            odoo_template_id = self._get_existing_product(product)
            odoo_category_id = self._get_category_product(product)
            odoo_uom_id = self._get_uom_product(product)

            payload = self._build_product_payload(product, odoo_category_id, odoo_uom_id)

            if odoo_template_id:
                print("sync_product: ",payload)
                
                _logger.info("Updating product.template id=%s for external product %s", odoo_template_id, product.maSanPham)
                self.odoo.write("product.template", [odoo_template_id], payload)
            else:
                _logger.info("Creating product.template for external product %s", product.maSanPham)
                parts =  product.maSanPham.split('-')
                if len(parts)==3:
                    payload['default_code'] = "-".join(product.maSanPham.split('-')[:2])
                # else:
                #     ids = self.odoo.search("product.template", [("default_code", "=", product.maSanPham)], limit=1)
                odoo_template_id = self.odoo.create("product.template", payload)

            # Ensure product.product variant exists
            variant_ids = self.odoo.search("product.product", [("product_tmpl_id", "=", odoo_template_id)], limit=1)
            if variant_ids:
                variant_id = variant_ids[0]
                _logger.info("Found product.product variant id=%s for template %s", variant_id, odoo_template_id)
                return variant_id
            else:
                _logger.info("Creating product.product variant for template %s", odoo_template_id)
                variant_payload = {"product_tmpl_id": odoo_template_id}
                variant_id = self.odoo.create("product.product", variant_payload)
                _logger.info("Created product.product id=%s", variant_id)
                return variant_id

        except Exception as e:
            _logger.exception("Failed to sync product %s: %s", getattr(product, "maSanPham", "<unknown>"), e)
            raise

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_existing_product(self, product: ApiWarehouse) -> Optional[int]:
        print("_get_existing_product: ",product)
        parts =  product.maSanPham.split('-')
        if len(parts)!=3:
            ids = self.odoo.search("product.template", [("default_code", "=", "-".join(parts[:2]))], limit=1)
        else:
            ids = self.odoo.search("product.template", [("default_code", "=", product.maSanPham)], limit=1)
        return ids[0] if ids else None

    def _get_category_product(self, product: ApiWarehouse) -> Optional[int]:
        if getattr(product, "maNhom", None):
            ids = self.odoo.search("product.category", [("x_category_code", "=", product.maNhom)], limit=1)
            if ids:
                return ids[0]
        return None

    def _get_uom_product(self, product: ApiWarehouse) -> Optional[int]:
        if getattr(product, "donViTinh", None):
            ids = self.odoo.search("uom.uom", [("name", "=", product.donViTinh)], limit=1)
            if ids:
                return ids[0]
        return None

    def _build_product_payload(self, product: ApiWarehouse, category_id: Optional[int], uom_id: Optional[int]) -> Dict[str, Any]:
        # parts = ids = self.odoo.search("product.template", [("default_code", "=", product.ma_tong)], limit=1)
        # else:
        #     ids = self.odoo.search("product.template", [("default_code", "=", product.maSanPham)], limit=1)
        
        payload: Dict[str, Any] = {
            "name": product.tenSanPham,
            "sale_ok": True,
            "purchase_ok": True,
            "type": "consu",
            "list_price": getattr(product, "giaBan", 0.0),
            "default_code": product.maSanPham if len(product.maSanPham.split('-')) <=3 else "-".join(parts[:2]),
            "barcode": getattr(product, "maVach", False),
            "categ_id": category_id,
            "uom_id": uom_id,
            "uom_po_id": uom_id,
            "gold_weight": getattr(product, "trongLuongKimLoai", 0.0),
            "stone_main_weight": getattr(product, "trongLuongDaChinh", 0.0),
            "secondary_stone_weight": getattr(product, "trongLuongDaPhu", 0.0),
            "stamp_weight": getattr(product, "trongLuongTem", 0.0),
            "labor_cost": getattr(product, "tienCongBan", 0.0),
            "stone_cost": getattr(product, "tienDaBan", 0.0),
            "x_old_code": getattr(product, "maSanPham", None),
            "available_in_pos": True,
        }

        cleaned = {k: v for k, v in payload.items() if v is not None}
        _logger.debug("Built product.template payload: %s", cleaned)
        return cleaned
