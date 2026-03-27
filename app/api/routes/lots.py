from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.domain.schemas.lot import LotCreate, LotRead, LotUpdateStatus
from app.repositories.lot import LotRepository
from app.services.lot_service import LotService

router = APIRouter(prefix="/api/v1/lots", tags=["lots"])


@router.post(
    "",
    response_model=LotRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lot(
    payload: LotCreate,
    session: AsyncSession = Depends(get_session),
) -> LotRead:
    repository = LotRepository(session)
    service = LotService(repository)
    lot = await service.create_lot(payload)
    return LotRead.model_validate(lot)


@router.get(
    "",
    response_model=list[LotRead],
)
async def list_lots(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[LotRead]:
    repository = LotRepository(session)
    service = LotService(repository)
    lots = await service.list_lots(limit=limit, offset=offset)
    return [LotRead.model_validate(item) for item in lots]


@router.get(
    "/{lot_id}",
    response_model=LotRead,
)
async def get_lot(
    lot_id: int,
    session: AsyncSession = Depends(get_session),
) -> LotRead:
    repository = LotRepository(session)
    service = LotService(repository)
    lot = await service.get_lot(lot_id)
    if lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )
    return LotRead.model_validate(lot)


@router.patch(
    "/{lot_id}/status",
    response_model=LotRead,
)
async def update_lot_status(
    lot_id: int,
    payload: LotUpdateStatus,
    session: AsyncSession = Depends(get_session),
) -> LotRead:
    repository = LotRepository(session)
    service = LotService(repository)
    lot = await service.set_status(lot_id=lot_id, status=payload.status)
    if lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )
    return LotRead.model_validate(lot)