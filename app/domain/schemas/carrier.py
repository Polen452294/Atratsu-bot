from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CarrierCandidate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    external_carrier_id: str | None = Field(default=None, max_length=100)
    carrier_name: str = Field(min_length=1, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    contact_nick: str | None = Field(default=None, max_length=100)
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    proposed_price: Decimal = Field(gt=0)
    vehicle_type: str = Field(min_length=1, max_length=100)
    available_at: datetime | None = None
    route_comment: str | None = Field(default=None, max_length=255)
    score: Decimal = Field(default=Decimal("0"))
    raw_payload: dict = Field(default_factory=dict)


class CarrierMatchRead(BaseModel):
    id: int
    lot_id: int
    provider: str
    external_carrier_id: str | None
    carrier_name: str
    contact_phone: str | None
    contact_nick: str | None
    rating: Decimal | None
    proposed_price: Decimal
    vehicle_type: str
    available_at: datetime | None
    route_comment: str | None
    score: Decimal
    is_selected: bool
    raw_payload: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)