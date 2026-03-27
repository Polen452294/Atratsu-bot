from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.lot import Lot
from app.domain.schemas.lot import LotCreate


class LotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: LotCreate) -> Lot:
        lot = Lot(
            external_source=data.external_source,
            external_id=data.external_id,
            route_from=data.route_from,
            route_to=data.route_to,
            distance_km=data.distance_km,
            deadline_at=data.deadline_at,
            vehicle_type=data.vehicle_type,
            weight_tons=data.weight_tons,
            volume_m3=data.volume_m3,
            budget_rub=data.budget_rub,
            created_by=data.created_by,
        )
        self.session.add(lot)
        await self.session.commit()
        await self.session.refresh(lot)
        return lot

    async def get_by_id(self, lot_id: int) -> Lot | None:
        stmt = select(Lot).where(Lot.id == lot_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Lot]:
        stmt = (
            select(Lot)
            .order_by(Lot.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, lot: Lot, status: str) -> Lot:
        lot.status = status
        await self.session.commit()
        await self.session.refresh(lot)
        return lot