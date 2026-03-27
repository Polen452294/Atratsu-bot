from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_deal_service, get_session
from app.domain.schemas.deal import DealRead
from app.services.deal_service import DealService

router = APIRouter(prefix="/api/v1", tags=["deals"])


@router.post(
    "/lots/{lot_id}/select/{match_id}",
    response_model=DealRead,
    status_code=status.HTTP_201_CREATED,
)
async def select_match_for_lot(
    lot_id: int,
    match_id: int,
    session: AsyncSession = Depends(get_session),
) -> DealRead:
    service = await get_deal_service(session)
    deal = await service.select_candidate(lot_id=lot_id, match_id=match_id)

    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot or match not found, or match does not belong to lot",
        )

    return deal


@router.post(
    "/deals/{deal_id}/initiate",
    response_model=DealRead,
    status_code=status.HTTP_200_OK,
)
async def initiate_deal(
    deal_id: int,
    session: AsyncSession = Depends(get_session),
) -> DealRead:
    service = await get_deal_service(session)
    deal = await service.initiate_deal(deal_id=deal_id)

    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    return deal


@router.get(
    "/deals/{deal_id}",
    response_model=DealRead,
    status_code=status.HTTP_200_OK,
)
async def get_deal(
    deal_id: int,
    session: AsyncSession = Depends(get_session),
) -> DealRead:
    service = await get_deal_service(session)
    deal = await service.get_deal(deal_id=deal_id)

    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )

    return deal