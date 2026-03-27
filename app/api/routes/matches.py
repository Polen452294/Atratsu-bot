from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_search_service, get_session
from app.domain.schemas.carrier import CarrierMatchRead
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/lots", tags=["matches"])


@router.post(
    "/{lot_id}/search",
    response_model=list[CarrierMatchRead],
    status_code=status.HTTP_200_OK,
)
async def search_matches_for_lot(
    lot_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> list[CarrierMatchRead]:
    service = await get_search_service(session)
    matches = await service.search_for_lot(lot_id=lot_id, limit=limit)

    if matches is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found",
        )

    return matches


@router.get(
    "/{lot_id}/matches",
    response_model=list[CarrierMatchRead],
    status_code=status.HTTP_200_OK,
)
async def get_matches_for_lot(
    lot_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> list[CarrierMatchRead]:
    service = await get_search_service(session)
    return await service.get_top_matches(lot_id=lot_id, limit=limit)