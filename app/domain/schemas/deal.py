from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DealCreate(BaseModel):
    lot_id: int = Field(gt=0)
    carrier_match_id: int = Field(gt=0)
    initiated_message: str | None = None


class DealRead(BaseModel):
    id: int
    lot_id: int
    carrier_match_id: int
    status: str
    initiated_message: str | None
    initiated_at: datetime
    confirmed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)