from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Operation
from app.schemas import OperationsPage

router = APIRouter()


@router.get("/operations", response_model=OperationsPage)
def list_operations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Operation))
    items = db.scalars(
        select(Operation)
        .order_by(Operation.created_at.desc(), Operation.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return OperationsPage(items=items, total=total, limit=limit, offset=offset)
