# utils/api_response.py
from rest_framework.response import Response

class ApiResponse:
    """
    Lớp đóng gói response chuẩn cho API
    Format:
    {
      "success": true/false,
      "message": "Thông điệp",
      "data": [...]
    }
    """

    @staticmethod
    def success(message="Thành công", data=None, status=200, pagination=None):
        response = {
            "success": True,
            "message": message,
            "data": data if data is not None else []
        }
        if pagination:
            response["pagination"] = pagination
        return Response(response, status=status)

    @staticmethod
    def error(message="Thất bại", data=None, status=400):
        return Response({
            "success": False,
            "message": message,
            "data": data if data is not None else []
        }, status=status)
