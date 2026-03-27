from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.carrier_match import CarrierMatch
from app.domain.schemas.carrier import CarrierCandidate


class CarrierMatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def delete_for_lot(self, lot_id: int) -> None:
        stmt = delete(CarrierMatch).where(CarrierMatch.lot_id == lot_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def bulk_create(
        self,
        lot_id: int,
        candidates: list[CarrierCandidate],
    ) -> list[CarrierMatch]:
        items: list[CarrierMatch] = []

        for candidate in candidates:
            raw_payload = candidate.raw_payload if candidate.raw_payload else None

            item = CarrierMatch(
                lot_id=lot_id,
                provider=candidate.provider,
                external_carrier_id=candidate.external_carrier_id,
                carrier_name=candidate.carrier_name,
                contact_phone=candidate.contact_phone,
                contact_nick=candidate.contact_nick,
                rating=candidate.rating,
                proposed_price=candidate.proposed_price,
                vehicle_type=candidate.vehicle_type,
                available_at=candidate.available_at,
                route_comment=candidate.route_comment,
                score=candidate.score,
                raw_payload=str(raw_payload) if raw_payload is not None else None,
            )
            items.append(item)

        self.session.add_all(items)
        await self.session.commit()

        for item in items:
            await self.session.refresh(item)

        return items

    async def list_by_lot_id(
        self,
        lot_id: int,
        limit: int = 5,
    ) -> list[CarrierMatch]:
        stmt = (
            select(CarrierMatch)
            .where(CarrierMatch.lot_id == lot_id)
            .order_by(
                CarrierMatch.score.desc(),
                CarrierMatch.proposed_price.asc(),
                CarrierMatch.created_at.asc(),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, match_id: int) -> CarrierMatch | None:
        stmt = select(CarrierMatch).where(CarrierMatch.id == match_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_selected_for_lot(self, lot_id: int) -> None:
        stmt = (
            update(CarrierMatch)
            .where(CarrierMatch.lot_id == lot_id)
            .values(is_selected=False)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def mark_selected(self, match_id: int) -> CarrierMatch | None:
        stmt = (
            update(CarrierMatch)
            .where(CarrierMatch.id == match_id)
            .values(is_selected=True)
            .returning(CarrierMatch)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()