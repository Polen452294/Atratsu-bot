import random
from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.schemas.lot import LotCreate


class MockAtrucksProvider:
    def generate_lot(self) -> LotCreate:
        routes = [
            ("Москва", "Санкт-Петербург"),
            ("Казань", "Екатеринбург"),
            ("Новосибирск", "Красноярск"),
        ]

        vehicle_types = ["реф", "тент", "фура"]

        route_from, route_to = random.choice(routes)

        return LotCreate(
            route_from=route_from,
            route_to=route_to,
            distance_km=random.randint(300, 2000),
            deadline_at=datetime.utcnow() + timedelta(days=random.randint(1, 5)),
            vehicle_type=random.choice(vehicle_types),
            weight_tons=Decimal(str(random.randint(5, 25))),
            volume_m3=Decimal(str(random.randint(30, 100))),
            budget_rub=Decimal(str(random.randint(50000, 120000))),
            external_source="mock_atrucks",
            external_id=str(random.randint(1000, 9999)),
        )