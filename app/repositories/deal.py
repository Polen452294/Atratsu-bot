from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.deal import Deal


class DealRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        lot_id: int,
        carrier_match_id: int,
        initiated_message: str | None = None,
    ) -> Deal:
        deal = Deal(
            lot_id=lot_id,
            carrier_match_id=carrier_match_id,
            initiated_message=initiated_message,
        )
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        return deal

    async def get_by_id(self, deal_id: int) -> Deal | None:
        stmt = select(Deal).where(Deal.id == deal_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_lot_id(self, lot_id: int) -> Deal | None:
        stmt = (
            select(Deal)
            .where(Deal.lot_id == lot_id)
            .order_by(Deal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()