from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CarrierMatch(Base):
    __tablename__ = "carrier_matches"

    id: Mapped[int] = mapped_column(primary_key=True)

    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id", ondelete="CASCADE"))

    provider: Mapped[str] = mapped_column(String(50))

    external_carrier_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    carrier_name: Mapped[str] = mapped_column(String(255))

    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_nick: Mapped[str | None] = mapped_column(String(100), nullable=True)

    rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)

    proposed_price: Mapped[float] = mapped_column(Numeric(12, 2))

    vehicle_type: Mapped[str] = mapped_column(String(100))

    available_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    route_comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    score: Mapped[float] = mapped_column(Numeric(6, 2), default=0)

    is_selected: Mapped[bool] = mapped_column(default=False)

    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )