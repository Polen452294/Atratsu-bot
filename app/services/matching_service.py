from datetime import datetime
from decimal import Decimal

from app.domain.schemas.carrier import CarrierCandidate
from app.domain.schemas.lot import LotRead


class MatchingService:
    def filter_candidates(
        self,
        lot: LotRead,
        candidates: list[CarrierCandidate],
    ) -> list[CarrierCandidate]:
        filtered: list[CarrierCandidate] = []

        for candidate in candidates:
            if not self._vehicle_matches(lot.vehicle_type, candidate.vehicle_type):
                continue

            if candidate.proposed_price > lot.budget_rub:
                continue

            if candidate.available_at and candidate.available_at > lot.deadline_at:
                continue

            filtered.append(candidate)

        return filtered

    def score_candidates(
        self,
        lot: LotRead,
        candidates: list[CarrierCandidate],
    ) -> list[CarrierCandidate]:
        scored: list[CarrierCandidate] = []

        for candidate in candidates:
            candidate.score = self._score_candidate(lot, candidate)
            scored.append(candidate)

        return scored

    def sort_candidates(
        self,
        candidates: list[CarrierCandidate],
    ) -> list[CarrierCandidate]:
        return sorted(
            candidates,
            key=lambda item: (
                item.score,
                -item.proposed_price,
            ),
            reverse=True,
        )

    def get_top_candidates(
        self,
        lot: LotRead,
        candidates: list[CarrierCandidate],
        limit: int = 5,
    ) -> list[CarrierCandidate]:
        filtered = self.filter_candidates(lot, candidates)
        scored = self.score_candidates(lot, filtered)
        sorted_candidates = self.sort_candidates(scored)
        return sorted_candidates[:limit]

    def _score_candidate(
        self,
        lot: LotRead,
        candidate: CarrierCandidate,
    ) -> Decimal:
        score = Decimal("0")

        score += self._vehicle_score(lot.vehicle_type, candidate.vehicle_type)
        score += self._price_score(lot.budget_rub, candidate.proposed_price)
        score += self._rating_score(candidate.rating)
        score += self._availability_score(lot.deadline_at, candidate.available_at)

        return score.quantize(Decimal("0.01"))

    def _vehicle_matches(
        self,
        lot_vehicle_type: str,
        candidate_vehicle_type: str,
    ) -> bool:
        return lot_vehicle_type.strip().lower() == candidate_vehicle_type.strip().lower()

    def _vehicle_score(
        self,
        lot_vehicle_type: str,
        candidate_vehicle_type: str,
    ) -> Decimal:
        if self._vehicle_matches(lot_vehicle_type, candidate_vehicle_type):
            return Decimal("30")
        return Decimal("0")

    def _price_score(
        self,
        budget: Decimal,
        proposed_price: Decimal,
    ) -> Decimal:
        if proposed_price > budget:
            return Decimal("0")

        ratio = proposed_price / budget

        if ratio <= Decimal("0.80"):
            return Decimal("35")
        if ratio <= Decimal("0.90"):
            return Decimal("30")
        if ratio <= Decimal("1.00"):
            return Decimal("20")

        return Decimal("0")

    def _rating_score(self, rating: Decimal | None) -> Decimal:
        if rating is None:
            return Decimal("5")
        if rating >= Decimal("4.8"):
            return Decimal("20")
        if rating >= Decimal("4.5"):
            return Decimal("15")
        if rating >= Decimal("4.0"):
            return Decimal("10")
        return Decimal("0")

    def _availability_score(
        self,
        deadline_at: datetime,
        available_at: datetime | None,
    ) -> Decimal:
        if available_at is None:
            return Decimal("5")

        if available_at <= deadline_at:
            return Decimal("15")

        return Decimal("0")