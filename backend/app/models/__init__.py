import enum
from datetime import datetime, timezone

from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(str, enum.Enum):
    transfer = "transfer"
    salary = "salary"
    groceries = "groceries"
    restaurants = "restaurants"
    transport = "transport"
    housing = "housing"
    utilities = "utilities"
    health = "health"
    entertainment = "entertainment"
    shopping = "shopping"
    travel = "travel"
    education = "education"
    subscriptions = "subscriptions"


class OperationStatus(str, enum.Enum):
    pending = "pending"
    done = "done"
    failed = "failed"


class OperationSource(str, enum.Enum):
    image = "image"
    audio = "audio"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[Category | None] = mapped_column(
        Enum(Category, native_enum=False), default=None
    )
    status: Mapped[OperationStatus] = mapped_column(
        Enum(OperationStatus, native_enum=False), default=OperationStatus.pending
    )
    source: Mapped[OperationSource] = mapped_column(Enum(OperationSource, native_enum=False))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), default=None)
    description: Mapped[str | None] = mapped_column(String, default=None)
    file_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
