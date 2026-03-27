from typing import Protocol

from app.domain.schemas.carrier import CarrierCandidate
from app.domain.schemas.lot import LotRead


class BaseAtiSuProvider(Protocol):
    async def search_carriers(self, lot: LotRead) -> list[CarrierCandidate]:
        ...