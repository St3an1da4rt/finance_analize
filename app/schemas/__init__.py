from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import Category, OperationSource, OperationStatus


class OperationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Category
    status: OperationStatus
    source: OperationSource
    created_at: datetime


class OperationsPage(BaseModel):
    items: list[OperationOut]
    total: int
    limit: int
    offset: int
