from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_export_service, get_session
from app.domain.schemas.export import ExportFileRead
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/v1/lots", tags=["exports"])


@router.post(
    "/{lot_id}/export/json",
    response_model=ExportFileRead,
    status_code=status.HTTP_201_CREATED,
)
async def export_lot_to_json(
    lot_id: int,
    session: AsyncSession = Depends(get_session),
) -> ExportFileRead:
    service = await get_export_service(session)
    export_file = await service.export_to_json(lot_id)

    if export_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )

    return export_file


@router.post(
    "/{lot_id}/export/csv",
    response_model=ExportFileRead,
    status_code=status.HTTP_201_CREATED,
)
async def export_lot_to_csv(
    lot_id: int,
    session: AsyncSession = Depends(get_session),
) -> ExportFileRead:
    service = await get_export_service(session)
    export_file = await service.export_to_csv(lot_id)

    if export_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )

    return export_file


@router.get(
    "/{lot_id}/exports",
    response_model=list[ExportFileRead],
    status_code=status.HTTP_200_OK,
)
async def list_lot_exports(
    lot_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[ExportFileRead]:
    service = await get_export_service(session)
    return await service.list_exports(lot_id)