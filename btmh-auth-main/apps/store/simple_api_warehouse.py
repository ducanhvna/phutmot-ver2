# simple_api_warehouse.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, Dict, Tuple


def _to_float(v: Any, default: float = 0.0) -> float:
    if v is None or v == "":
        return default
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).replace(",", ""))
        except Exception:
            return default


def _to_int(v: Any, default: int = 0) -> int:
    if v is None or v == "":
        return default
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return default


def _parse_datetime(v: Any) -> Optional[datetime]:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    s = str(v).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    try:
        ts = int(float(s))
        return datetime.fromtimestamp(ts)
    except Exception:
        return None


class ApiWarehouse:
    """
    Simple container for product warehouse info (no external deps).
    Usage:
        obj = ApiWarehouse.from_dict(api_response.get("data", {}))
    """

    def __init__(
        self,
        id: int,
        maSanPham: str,
        tenSanPham: str,
        ma_tong: str,
        maVach: Optional[str] = None,
        donViTinh: Optional[str] = None,
        maNhom: Optional[str] = None,
        ngayNhap: Optional[datetime] = None,
        giaBan: float = 0.0,
        trongLuongKimLoai: float = 0.0,
        ton_kho: int = 0,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.id = int(id)
        self.maSanPham = maSanPham
        self.tenSanPham = tenSanPham
        self.maVach = maVach
        self.donViTinh = donViTinh
        self.maNhom = maNhom
        self.ngayNhap = ngayNhap
        self.giaBan = giaBan
        self.trongLuongKimLoai = trongLuongKimLoai
        self.ton_kho = ton_kho
        self.ma_tong = ma_tong
        self._raw = raw or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiWarehouse":
        """
        Build a simple ApiWarehouse from a dict (API payload).
        Only extracts commonly used fields; safe defaults applied.
        """
        if data is None:
            raise ValueError("data is None")

        id_val = _to_int(data.get("id"), 0)
        maSanPham = str(data.get("maSanPham") or data.get("code") or "")
        tenSanPham = str(data.get("tenSanPham") or data.get("name") or "")
        maVach = data.get("maVach") or data.get("barcode")
        donViTinh = data.get("donViTinh") or data.get("uom")
        maNhom = data.get("maNhom")
        ngayNhap = _parse_datetime(data.get("ngayNhap") or data.get("ngay_nhap"))
        giaBan = _to_float(data.get("giaBan"), 0.0)
        trongLuongKimLoai = _to_float(data.get("trongLuongKimLoai"), 0.0)
        ton_kho = _to_int(data.get("ton_kho"), 0)
        ma_tong = _to_int(data.get("ma_tong"), None)

        return cls(
            id=id_val,
            maSanPham=maSanPham,
            tenSanPham=tenSanPham,
            maVach=maVach,
            donViTinh=donViTinh,
            maNhom=maNhom,
            ngayNhap=ngayNhap,
            giaBan=giaBan,
            trongLuongKimLoai=trongLuongKimLoai,
            ton_kho=ton_kho,
            ma_tong=ma_tong,
            raw=dict(data),
        )

    def sku_and_serial_from_code(self, code: Optional[str]) -> Tuple[str, Optional[str]]:
        """
        Nếu code.split('-') có 3 phần:
            sku = phần1 + '-' + phần2
            serial = full code
        Ngược lại:
            sku = full code
            serial = None
        """
        if not code:
            return ("", None)
        parts = str(code).split("-")
        if len(parts) == 3:
            return ("-".join(parts[:2]), code)
        return (code, None)

    def to_dict(self) -> Dict[str, Any]:
        """
        Trả về dict đơn giản (loại bỏ trường nội bộ).
        """
        out = {
            "id": self.id,
            "maSanPham": self.maSanPham,
            "tenSanPham": self.tenSanPham,
            "maVach": self.maVach,
            "donViTinh": self.donViTinh,
            "maNhom": self.maNhom,
            "ngayNhap": self.ngayNhap.strftime("%Y-%m-%d %H:%M:%S") if self.ngayNhap else None,
            "giaBan": self.giaBan,
            "trongLuongKimLoai": self.trongLuongKimLoai,
            "ton_kho": self.ton_kho,
            "ma_tong": self.ma_tong
        }
        # remove None values
        return {k: v for k, v in out.items() if v is not None}

    def __repr__(self) -> str:
        return f"<ApiWarehouse {self.maSanPham} - {self.tenSanPham} (id={self.id})>"
