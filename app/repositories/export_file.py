from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.export_file import ExportFile


class ExportFileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        lot_id: int,
        format: str,
        file_path: str | None = None,
        payload_json: str | None = None,
    ) -> ExportFile:
        export_file = ExportFile(
            lot_id=lot_id,
            format=format,
            file_path=file_path,
            payload_json=payload_json,
        )
        self.session.add(export_file)
        await self.session.commit()
        await self.session.refresh(export_file)
        return export_file

    async def get_by_id(self, export_id: int) -> ExportFile | None:
        stmt = select(ExportFile).where(ExportFile.id == export_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_lot_id(self, lot_id: int) -> list[ExportFile]:
        stmt = (
            select(ExportFile)
            .where(ExportFile.lot_id == lot_id)
            .order_by(ExportFile.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())