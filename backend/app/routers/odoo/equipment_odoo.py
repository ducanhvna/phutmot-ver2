from fastapi import APIRouter, HTTPException
from app.utils.education.realtendant import get_all_equipments

router = APIRouter(prefix="/api/odoo", tags=["odoo"])

@router.get("/equipments")
def get_equipments():
    try:
        equipments = get_all_equipments()
        return equipments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/equipments/{equipment_id}")
def get_equipment_detail(equipment_id: int):
    try:
        # get_all_equipments không có hàm lấy theo id, nên lấy tất cả rồi lọc
        equipments = get_all_equipments()
        equipment = next((item for item in equipments if item['id'] == equipment_id), None)
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        return equipment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
