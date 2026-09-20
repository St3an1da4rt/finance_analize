import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(str, enum.Enum):
    transfer = "transfer"
    salary = "salary"
    other = "other"
    uncategorized = "uncategorized"


class OperationStatus(str, enum.Enum):
    pending = "pending"


class OperationSource(str, enum.Enum):
    image = "image"
    audio = "audio"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[Category] = mapped_column(
        Enum(Category, native_enum=False), default=Category.uncategorized
    )
    status: Mapped[OperationStatus] = mapped_column(
        Enum(OperationStatus, native_enum=False), default=OperationStatus.pending
    )
    source: Mapped[OperationSource] = mapped_column(Enum(OperationSource, native_enum=False))
    file_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
