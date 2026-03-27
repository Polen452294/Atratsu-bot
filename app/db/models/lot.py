from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.enums import LotStatus


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(primary_key=True)

    external_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    route_from: Mapped[str] = mapped_column(String(255))
    route_to: Mapped[str] = mapped_column(String(255))

    distance_km: Mapped[int] = mapped_column(Integer)

    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    vehicle_type: Mapped[str] = mapped_column(String(100))

    weight_tons: Mapped[float] = mapped_column(Numeric(10, 2))
    volume_m3: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    budget_rub: Mapped[float] = mapped_column(Numeric(12, 2))

    status: Mapped[str] = mapped_column(
        String(50),
        default=LotStatus.CREATED.value,
    )

    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )