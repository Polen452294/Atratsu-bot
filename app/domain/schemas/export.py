from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExportFileCreate(BaseModel):
    lot_id: int = Field(gt=0)
    format: str = Field(min_length=1, max_length=20)
    file_path: str | None = Field(default=None, max_length=500)
    payload_json: str | None = None


class ExportFileRead(BaseModel):
    id: int
    lot_id: int
    format: str
    file_path: str | None
    payload_json: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)