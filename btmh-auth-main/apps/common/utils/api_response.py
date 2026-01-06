from rest_framework.response import Response

class ApiResponse:
    """
    Lớp đóng gói response chuẩn cho API
    Format:
    {
      "success": true/false,
      "message": "Thông điệp",
      "data": [...],
      "metadata": {...},
      "pagination": {...}
    }
    """

    @staticmethod
    def success(message="Thành công", data=None, status=200, pagination=None, metadata=None):
        response = {
            "success": True,
            "message": message,
            "data": data if data is not None else [],
            "metadata": metadata if metadata else {}
        }
        if pagination:
            response["pagination"] = pagination
        return Response(response, status=status)

    @staticmethod
    def error(message="Thất bại", data=None, status=400, metadata=None):
        return Response({
            "success": False,
            "message": message,
            "data": data if data is not None else [],
            "metadata": metadata if metadata else {}
        }, status=status)
