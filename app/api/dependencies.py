from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.integrations.ati_su.mock import MockAtiSuProvider
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.deal import DealRepository
from app.repositories.lot import LotRepository
from app.services.deal_service import DealService
from app.services.lot_service import LotService
from app.services.matching_service import MatchingService
from app.services.search_service import SearchService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_lot_service(
    session: AsyncSession,
) -> LotService:
    repository = LotRepository(session)
    return LotService(repository)


async def get_search_service(
    session: AsyncSession,
) -> SearchService:
    lot_repository = LotRepository(session)
    carrier_match_repository = CarrierMatchRepository(session)
    matching_service = MatchingService()
    provider = MockAtiSuProvider()

    return SearchService(
        lot_repository=lot_repository,
        carrier_match_repository=carrier_match_repository,
        matching_service=matching_service,
        provider=provider,
    )


async def get_deal_service(
    session: AsyncSession,
) -> DealService:
    lot_repository = LotRepository(session)
    carrier_match_repository = CarrierMatchRepository(session)
    deal_repository = DealRepository(session)

    return DealService(
        lot_repository=lot_repository,
        carrier_match_repository=carrier_match_repository,
        deal_repository=deal_repository,
    )