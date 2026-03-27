import logging

from app.db.enums import LotStatus
from app.domain.schemas.carrier import CarrierMatchRead
from app.domain.schemas.lot import LotRead
from app.integrations.ati_su.base import BaseAtiSuProvider
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.lot import LotRepository
from app.services.matching_service import MatchingService

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        lot_repository: LotRepository,
        carrier_match_repository: CarrierMatchRepository,
        matching_service: MatchingService,
        provider: BaseAtiSuProvider,
    ) -> None:
        self.lot_repository = lot_repository
        self.carrier_match_repository = carrier_match_repository
        self.matching_service = matching_service
        self.provider = provider

    async def search_for_lot(
        self,
        lot_id: int,
        limit: int = 5,
    ) -> list[CarrierMatchRead] | None:
        lot = await self.lot_repository.get_by_id(lot_id)
        if lot is None:
            logger.warning("Lot id=%s not found for search", lot_id)
            return None

        await self.lot_repository.update_status(lot, LotStatus.SEARCHING.value)

        lot_schema = LotRead.model_validate(lot)
        raw_candidates = await self.provider.search_carriers(lot_schema)

        logger.info(
            "Provider returned %s candidates for lot id=%s",
            len(raw_candidates),
            lot_id,
        )

        top_candidates = self.matching_service.get_top_candidates(
            lot=lot_schema,
            candidates=raw_candidates,
            limit=limit,
        )

        await self.carrier_match_repository.delete_for_lot(lot_id)
        created_matches = await self.carrier_match_repository.bulk_create(
            lot_id=lot_id,
            candidates=top_candidates,
        )

        if created_matches:
            await self.lot_repository.update_status(lot, LotStatus.CANDIDATES_FOUND.value)
        else:
            await self.lot_repository.update_status(lot, LotStatus.NO_CANDIDATES.value)

        return [CarrierMatchRead.model_validate(item) for item in created_matches]

    async def get_top_matches(
        self,
        lot_id: int,
        limit: int = 5,
    ) -> list[CarrierMatchRead]:
        matches = await self.carrier_match_repository.list_by_lot_id(
            lot_id=lot_id,
            limit=limit,
        )
        return [CarrierMatchRead.model_validate(item) for item in matches]