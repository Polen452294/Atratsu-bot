from datetime import timedelta
from decimal import Decimal

from app.domain.schemas.carrier import CarrierCandidate
from app.domain.schemas.lot import LotRead


class MockAtiSuProvider:
    async def search_carriers(self, lot: LotRead) -> list[CarrierCandidate]:
        deadline = lot.deadline_at

        return [
            CarrierCandidate(
                provider="mock_ati_su",
                external_carrier_id="carrier_001",
                carrier_name='ООО "ТрансЛайн"',
                contact_phone="+7 900 111-11-11",
                contact_nick="@transline",
                rating=Decimal("4.80"),
                proposed_price=Decimal("65000"),
                vehicle_type=lot.vehicle_type,
                available_at=deadline - timedelta(hours=8),
                route_comment=f"{lot.route_from} -> {lot.route_to}",
                raw_payload={
                    "source": "mock",
                    "position": 1,
                },
            ),
            CarrierCandidate(
                provider="mock_ati_su",
                external_carrier_id="carrier_002",
                carrier_name='ИП "ГрузЭкспресс"',
                contact_phone="+7 900 222-22-22",
                contact_nick="@gruzexpress",
                rating=Decimal("4.55"),
                proposed_price=Decimal("68000"),
                vehicle_type=lot.vehicle_type,
                available_at=deadline - timedelta(hours=5),
                route_comment=f"{lot.route_from} -> {lot.route_to}",
                raw_payload={
                    "source": "mock",
                    "position": 2,
                },
            ),
            CarrierCandidate(
                provider="mock_ati_su",
                external_carrier_id="carrier_003",
                carrier_name='ООО "Север Логистик"',
                contact_phone="+7 900 333-33-33",
                contact_nick="@severlog",
                rating=Decimal("4.20"),
                proposed_price=Decimal("70000"),
                vehicle_type=lot.vehicle_type,
                available_at=deadline - timedelta(hours=2),
                route_comment=f"{lot.route_from} -> {lot.route_to}",
                raw_payload={
                    "source": "mock",
                    "position": 3,
                },
            ),
            CarrierCandidate(
                provider="mock_ati_su",
                external_carrier_id="carrier_004",
                carrier_name='ООО "Магистраль"',
                contact_phone="+7 900 444-44-44",
                contact_nick="@magistral",
                rating=Decimal("4.90"),
                proposed_price=Decimal("72000"),
                vehicle_type=lot.vehicle_type,
                available_at=deadline - timedelta(hours=10),
                route_comment=f"{lot.route_from} -> {lot.route_to}",
                raw_payload={
                    "source": "mock",
                    "position": 4,
                },
            ),
            CarrierCandidate(
                provider="mock_ati_su",
                external_carrier_id="carrier_005",
                carrier_name='ООО "ЮгТранс"',
                contact_phone="+7 900 555-55-55",
                contact_nick="@yugtrans",
                rating=Decimal("3.90"),
                proposed_price=Decimal("61000"),
                vehicle_type="тент" if lot.vehicle_type != "тент" else lot.vehicle_type,
                available_at=deadline - timedelta(hours=6),
                route_comment=f"{lot.route_from} -> {lot.route_to}",
                raw_payload={
                    "source": "mock",
                    "position": 5,
                },
            ),
        ]