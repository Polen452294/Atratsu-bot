import logging

from app.domain.schemas.lot import LotCreate
from app.repositories.lot import LotRepository

logger = logging.getLogger(__name__)


class LotService:
    def __init__(self, lot_repository: LotRepository) -> None:
        self.lot_repository = lot_repository

    async def create_lot(self, data: LotCreate):
        logger.info(
            "Creating lot: %s -> %s, vehicle=%s, budget=%s",
            data.route_from,
            data.route_to,
            data.vehicle_type,
            data.budget_rub,
        )
        return await self.lot_repository.create(data)

    async def get_lot(self, lot_id: int):
        logger.info("Fetching lot id=%s", lot_id)
        return await self.lot_repository.get_by_id(lot_id)

    async def list_lots(self, limit: int = 100, offset: int = 0):
        logger.info("Listing lots limit=%s offset=%s", limit, offset)
        return await self.lot_repository.list_all(limit=limit, offset=offset)

    async def set_status(self, lot_id: int, status: str):
        lot = await self.lot_repository.get_by_id(lot_id)
        if lot is None:
            logger.warning("Lot id=%s not found for status update", lot_id)
            return None

        logger.info("Updating lot id=%s status=%s", lot_id, status)
        return await self.lot_repository.update_status(lot, status)