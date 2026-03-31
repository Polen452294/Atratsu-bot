import csv
import json
from pathlib import Path

from app.db.enums import ExportFormat, LotStatus
from app.domain.schemas.export import ExportFileRead
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.deal import DealRepository
from app.repositories.export_file import ExportFileRepository
from app.repositories.lot import LotRepository


class ExportService:
    def __init__(
        self,
        lot_repository: LotRepository,
        deal_repository: DealRepository,
        carrier_match_repository: CarrierMatchRepository,
        export_file_repository: ExportFileRepository,
        export_dir: str,
    ) -> None:
        self.lot_repository = lot_repository
        self.deal_repository = deal_repository
        self.carrier_match_repository = carrier_match_repository
        self.export_file_repository = export_file_repository
        self.export_dir = Path(export_dir)

    async def export_to_json(self, lot_id: int) -> ExportFileRead | None:
        lot = await self.lot_repository.get_by_id(lot_id)
        if lot is None:
            return None

        payload = await self._build_export_payload(lot_id)

        self.export_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.export_dir / f"lot_{lot_id}.json"
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        export_file = await self.export_file_repository.create(
            lot_id=lot_id,
            format=ExportFormat.JSON.value,
            file_path=str(file_path),
            payload_json=json.dumps(payload, ensure_ascii=False, default=str),
        )

        await self.lot_repository.update_status(lot, LotStatus.EXPORTED.value)

        return ExportFileRead.model_validate(export_file)

    async def export_to_csv(self, lot_id: int) -> ExportFileRead | None:
        lot = await self.lot_repository.get_by_id(lot_id)
        if lot is None:
            return None

        payload = await self._build_export_payload(lot_id)

        self.export_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.export_dir / f"lot_{lot_id}.csv"

        with file_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["field", "value"])

            for key, value in payload.items():
                if isinstance(value, dict):
                    for nested_key, nested_value in value.items():
                        writer.writerow([f"{key}.{nested_key}", nested_value])
                else:
                    writer.writerow([key, value])

        export_file = await self.export_file_repository.create(
            lot_id=lot_id,
            format=ExportFormat.CSV.value,
            file_path=str(file_path),
            payload_json=json.dumps(payload, ensure_ascii=False, default=str),
        )

        await self.lot_repository.update_status(lot, LotStatus.EXPORTED.value)

        return ExportFileRead.model_validate(export_file)

    async def list_exports(self, lot_id: int) -> list[ExportFileRead]:
        exports = await self.export_file_repository.list_by_lot_id(lot_id)
        return [ExportFileRead.model_validate(item) for item in exports]

    async def _build_export_payload(self, lot_id: int) -> dict:
        lot = await self.lot_repository.get_by_id(lot_id)
        deal = await self.deal_repository.get_by_lot_id(lot_id)

        if lot is None:
            raise ValueError("Lot not found")

        selected_carrier = None

        if deal is not None:
            match = await self.carrier_match_repository.get_by_id(deal.carrier_match_id)
            if match is not None:
                selected_carrier = {
                    "carrier_match_id": match.id,
                    "carrier_name": match.carrier_name,
                    "contact_phone": match.contact_phone,
                    "contact_nick": match.contact_nick,
                    "rating": str(match.rating) if match.rating is not None else None,
                    "proposed_price": str(match.proposed_price),
                    "vehicle_type": match.vehicle_type,
                }

        return {
            "lot_id": lot.id,
            "external_source": lot.external_source,
            "external_id": lot.external_id,
            "route_from": lot.route_from,
            "route_to": lot.route_to,
            "distance_km": lot.distance_km,
            "deadline_at": lot.deadline_at.isoformat(),
            "vehicle_type": lot.vehicle_type,
            "weight_tons": str(lot.weight_tons),
            "volume_m3": str(lot.volume_m3) if lot.volume_m3 is not None else None,
            "budget_rub": str(lot.budget_rub),
            "status": lot.status,
            "created_by": lot.created_by,
            "selected_carrier": selected_carrier,
        }