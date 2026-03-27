import logging

from app.db.enums import DealStatus, LotStatus
from app.domain.schemas.deal import DealRead
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.deal import DealRepository
from app.repositories.lot import LotRepository

logger = logging.getLogger(__name__)


class DealService:
    def __init__(
        self,
        lot_repository: LotRepository,
        carrier_match_repository: CarrierMatchRepository,
        deal_repository: DealRepository,
    ) -> None:
        self.lot_repository = lot_repository
        self.carrier_match_repository = carrier_match_repository
        self.deal_repository = deal_repository

    async def select_candidate(
        self,
        lot_id: int,
        match_id: int,
    ) -> DealRead | None:
        lot = await self.lot_repository.get_by_id(lot_id)
        if lot is None:
            logger.warning("Lot id=%s not found for deal creation", lot_id)
            return None

        match = await self.carrier_match_repository.get_by_id(match_id)
        if match is None:
            logger.warning("Match id=%s not found for deal creation", match_id)
            return None

        if match.lot_id != lot_id:
            logger.warning(
                "Match id=%s does not belong to lot id=%s",
                match_id,
                lot_id,
            )
            return None

        await self.carrier_match_repository.clear_selected_for_lot(lot_id)
        selected_match = await self.carrier_match_repository.mark_selected(match_id)

        if selected_match is None:
            logger.warning("Failed to mark match id=%s as selected", match_id)
            return None

        initiated_message = self._build_initiated_message(
            route_from=lot.route_from,
            route_to=lot.route_to,
            weight_tons=lot.weight_tons,
            vehicle_type=lot.vehicle_type,
            proposed_price=selected_match.proposed_price,
        )

        deal = await self.deal_repository.create(
            lot_id=lot_id,
            carrier_match_id=match_id,
            initiated_message=initiated_message,
        )

        await self.lot_repository.update_status(lot, LotStatus.SELECTED.value)

        logger.info(
            "Created deal id=%s for lot id=%s with match id=%s",
            deal.id,
            lot_id,
            match_id,
        )

        return DealRead.model_validate(deal)

    async def initiate_deal(
        self,
        deal_id: int,
    ) -> DealRead | None:
        deal = await self.deal_repository.get_by_id(deal_id)
        if deal is None:
            logger.warning("Deal id=%s not found for initiation", deal_id)
            return None

        lot = await self.lot_repository.get_by_id(deal.lot_id)
        if lot is not None:
            await self.lot_repository.update_status(lot, LotStatus.DEAL_INITIATED.value)

        deal.status = DealStatus.INITIATED.value
        await self.deal_repository.session.commit()
        await self.deal_repository.session.refresh(deal)

        logger.info("Deal id=%s initiated", deal_id)

        return DealRead.model_validate(deal)

    async def get_deal(self, deal_id: int) -> DealRead | None:
        deal = await self.deal_repository.get_by_id(deal_id)
        if deal is None:
            return None
        return DealRead.model_validate(deal)

    def _build_initiated_message(
        self,
        route_from: str,
        route_to: str,
        weight_tons,
        vehicle_type: str,
        proposed_price,
    ) -> str:
        return (
            f"Предлагаем рейс {route_from} - {route_to}, "
            f"{weight_tons}т {vehicle_type}, {proposed_price} руб. "
            f"Готовы подтвердить перевозку?"
        )