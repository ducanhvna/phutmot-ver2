from fastapi import APIRouter, HTTPException
from app.utils.education.realtendant import get_all_mrp_productions, get_mrp_production_detail

router = APIRouter(prefix="/api/odoo", tags=["odoo"])

@router.get("/mrp_productions")
def get_mrp_productions():
    try:
        productions = get_all_mrp_productions()
        return productions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mrp_productions/{production_id}")
def get_mrp_production_detail_api(production_id: int):
    try:
        production = get_mrp_production_detail(production_id)
        if not production:
            raise HTTPException(status_code=404, detail="Production not found")
        return production
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
