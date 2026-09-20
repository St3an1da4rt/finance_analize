from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Operation
from app.schemas import OperationsPage

router = APIRouter()


def _utc(dt: datetime | None) -> datetime | None:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/operations", response_model=OperationsPage)
def list_operations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    date_from: datetime | None = Query(None, description="created_at >= (naive = UTC)"),
    date_to: datetime | None = Query(None, description="created_at <= (naive = UTC)"),
    db: Session = Depends(get_db),
):
    date_from, date_to = _utc(date_from), _utc(date_to)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must be <= date_to")

    filters = []
    if date_from:
        filters.append(Operation.created_at >= date_from)
    if date_to:
        filters.append(Operation.created_at <= date_to)

    total = db.scalar(select(func.count()).select_from(Operation).where(*filters))
    items = db.scalars(
        select(Operation)
        .where(*filters)
        .order_by(Operation.created_at.desc(), Operation.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return OperationsPage(items=items, total=total, limit=limit, offset=offset)
