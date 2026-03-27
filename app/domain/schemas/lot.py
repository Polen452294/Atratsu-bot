from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LotCreate(BaseModel):
    route_from: str = Field(min_length=1, max_length=255)
    route_to: str = Field(min_length=1, max_length=255)
    distance_km: int = Field(gt=0)
    deadline_at: datetime
    vehicle_type: str = Field(min_length=1, max_length=100)
    weight_tons: Decimal = Field(gt=0)
    volume_m3: Decimal | None = Field(default=None, gt=0)
    budget_rub: Decimal = Field(gt=0)
    external_source: str | None = Field(default="manual", max_length=50)
    external_id: str | None = Field(default=None, max_length=100)
    created_by: str | None = Field(default=None, max_length=100)


class LotUpdateStatus(BaseModel):
    status: str = Field(min_length=1, max_length=50)


class LotRead(BaseModel):
    id: int
    external_source: str | None
    external_id: str | None
    route_from: str
    route_to: str
    distance_km: int
    deadline_at: datetime
    vehicle_type: str
    weight_tons: Decimal
    volume_m3: Decimal | None
    budget_rub: Decimal
    status: str
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)