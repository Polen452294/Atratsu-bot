from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.texts.messages import MATCH_SELECTED
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.deal import DealRepository
from app.repositories.lot import LotRepository
from app.services.deal_service import DealService

router = Router()


@router.callback_query(F.data.startswith("match:select:"))
async def cb_select_match(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    parts = callback.data.split(":")
    match_id = int(parts[-1])

    carrier_match_repository = CarrierMatchRepository(session)
    match = await carrier_match_repository.get_by_id(match_id)

    if match is None:
        await callback.message.answer("Кандидат не найден.")
        await callback.answer()
        return

    service = DealService(
        lot_repository=LotRepository(session),
        carrier_match_repository=carrier_match_repository,
        deal_repository=DealRepository(session),
    )

    deal = await service.select_candidate(lot_id=match.lot_id, match_id=match.id)

    if deal is None:
        await callback.message.answer("Не удалось создать сделку.")
        await callback.answer()
        return

    await callback.message.answer(
        f"{MATCH_SELECTED}\n\n"
        f"Deal ID: {deal.id}\n"
        f"Сообщение перевозчику:\n{deal.initiated_message}"
    )
    await callback.answer()