from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class ApiResponseMiddleware(MiddlewareMixin):
    """
    Middleware chuẩn hóa tất cả response từ DRF.
    Nếu response chưa có format chuẩn, sẽ tự động wrap lại.
    """

    def process_response(self, request, response):
        if isinstance(response, Response):
            # Nếu response đã chuẩn hóa (có success) thì bỏ qua
            if isinstance(response.data, dict) and "success" in response.data:
                return response

            # Chuẩn hóa lại
            formatted = {
                "success": response.status_code < 400,
                "message": "",
                "data": response.data if response.data is not None else [],
                "metadata": {
                    "status_code": response.status_code,
                    "path": request.path,
                    "method": request.method,
                }
            }

            # Nếu có phân trang (DRF Pagination)
            if isinstance(response.data, dict) and "results" in response.data:
                formatted["data"] = response.data.get("results", [])
                formatted["pagination"] = {
                    "count": response.data.get("count"),
                    "next": response.data.get("next"),
                    "previous": response.data.get("previous"),
                }

            response.data = formatted
            response._is_rendered = False  # buộc DRF render lại
        return response
