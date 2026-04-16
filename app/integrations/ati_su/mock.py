import random
from datetime import timedelta
from decimal import Decimal

from app.domain.schemas.carrier import CarrierCandidate
from app.domain.schemas.lot import LotRead


class MockAtiSuProvider:
    def __init__(self, mode: str = "normal") -> None:
        self.mode = mode

    async def search_carriers(self, lot: LotRead) -> list[CarrierCandidate]:
        if self.mode == "empty":
            return []

        if self.mode == "bad_prices":
            return self._generate_bad_price_candidates(lot)

        return self._generate_normal_candidates(lot)

    def _generate_normal_candidates(self, lot: LotRead):
        return [
            self._build_candidate(lot, i)
            for i in range(random.randint(3, 7))
        ]

    def _generate_bad_price_candidates(self, lot: LotRead):
        candidates = []
        for i in range(5):
            candidate = self._build_candidate(lot, i)
            candidate.proposed_price = lot.budget_rub + Decimal("10000")
            candidates.append(candidate)
        return candidates

    def _build_candidate(self, lot: LotRead, idx: int) -> CarrierCandidate:
        price = Decimal(random.randint(50000, 90000))
        rating = Decimal(str(round(random.uniform(3.5, 5.0), 2)))

        return CarrierCandidate(
            provider="mock_ati",
            external_carrier_id=f"carrier_{idx}",
            carrier_name=f"Перевозчик #{idx}",
            contact_phone=f"+7 900 000-00-{idx:02d}",
            contact_nick=f"@carrier{idx}",
            rating=rating,
            proposed_price=price,
            vehicle_type=lot.vehicle_type,
            available_at=lot.deadline_at - timedelta(hours=random.randint(1, 10)),
            route_comment=f"{lot.route_from}->{lot.route_to}",
            raw_payload={"mock": True},
        )