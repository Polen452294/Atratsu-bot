from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.lots import lot_actions_keyboard, lot_list_keyboard
from app.bot.keyboards.matches import matches_with_export_keyboard
from app.bot.texts.messages import EXPORT_CREATED, LOT_NOT_FOUND, NO_LOTS_FOUND, NO_MATCHES_FOUND
from app.core.config import settings
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.deal import DealRepository
from app.repositories.export_file import ExportFileRepository
from app.repositories.lot import LotRepository
from app.services.export_service import ExportService
from app.services.lot_service import LotService
from app.services.matching_service import MatchingService
from app.services.search_service import SearchService
from app.integrations.ati_su.mock import MockAtiSuProvider

router = Router()


def _format_lot_card(lot) -> str:
    return (
        f"Лот #{lot.id}\n"
        f"Маршрут: {lot.route_from} -> {lot.route_to}\n"
        f"Км: {lot.distance_km}\n"
        f"Дедлайн: {lot.deadline_at}\n"
        f"Тип ТС: {lot.vehicle_type}\n"
        f"Вес: {lot.weight_tons} т\n"
        f"Объём: {lot.volume_m3 or '-'} м³\n"
        f"Бюджет: {lot.budget_rub} ₽\n"
        f"Статус: {lot.status}"
    )


def _format_matches(matches: list) -> str:
    lines = ["Найденные варианты:", ""]

    for index, match in enumerate(matches, start=1):
        lines.extend(
            [
                f"{index}. {match.carrier_name}",
                f"Цена: {match.proposed_price} ₽",
                f"Рейтинг: {match.rating or '-'}",
                f"Контакт: {match.contact_phone or match.contact_nick or '-'}",
                f"Score: {match.score}",
                "",
            ]
        )

    return "\n".join(lines).strip()


def _build_search_service(session: AsyncSession) -> SearchService:
    return SearchService(
        lot_repository=LotRepository(session),
        carrier_match_repository=CarrierMatchRepository(session),
        matching_service=MatchingService(),
        provider=MockAtiSuProvider(),
    )


def _build_export_service(session: AsyncSession) -> ExportService:
    return ExportService(
        lot_repository=LotRepository(session),
        deal_repository=DealRepository(session),
        carrier_match_repository=CarrierMatchRepository(session),
        export_file_repository=ExportFileRepository(session),
        export_dir=settings.export_dir,
    )


@router.message(F.text == "/my_lots")
async def cmd_my_lots(message: Message, session: AsyncSession) -> None:
    service = LotService(LotRepository(session))
    lots = await service.list_lots(limit=20, offset=0)

    if not lots:
        await message.answer(NO_LOTS_FOUND)
        return

    await message.answer(
        "Последние лоты:",
        reply_markup=lot_list_keyboard([lot.id for lot in lots]),
    )


@router.callback_query(F.data.startswith("lot:open:"))
async def cb_open_lot(callback: CallbackQuery, session: AsyncSession) -> None:
    lot_id = int(callback.data.split(":")[-1])

    service = LotService(LotRepository(session))
    lot = await service.get_lot(lot_id)

    if lot is None:
        await callback.message.answer(LOT_NOT_FOUND)
        await callback.answer()
        return

    await callback.message.answer(
        _format_lot_card(lot),
        reply_markup=lot_actions_keyboard(lot.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lot:matches:"))
async def cb_show_lot_matches(callback: CallbackQuery, session: AsyncSession) -> None:
    lot_id = int(callback.data.split(":")[-1])

    search_service = _build_search_service(session)
    matches = await search_service.get_top_matches(lot_id=lot_id, limit=5)

    if not matches:
        await callback.message.answer(NO_MATCHES_FOUND)
        await callback.answer()
        return

    await callback.message.answer(
        _format_matches(matches),
        reply_markup=matches_with_export_keyboard(lot_id, [item.id for item in matches]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lot:export:json:"))
async def cb_export_json(callback: CallbackQuery, session: AsyncSession) -> None:
    lot_id = int(callback.data.split(":")[-1])

    service = _build_export_service(session)
    export_file = await service.export_to_json(lot_id)

    if export_file is None or export_file.file_path is None:
        await callback.message.answer(LOT_NOT_FOUND)
        await callback.answer()
        return

    path = Path(export_file.file_path)
    await callback.message.answer(EXPORT_CREATED)
    await callback.message.answer_document(FSInputFile(path))
    await callback.answer()


@router.callback_query(F.data.startswith("lot:export:csv:"))
async def cb_export_csv(callback: CallbackQuery, session: AsyncSession) -> None:
    lot_id = int(callback.data.split(":")[-1])

    service = _build_export_service(session)
    export_file = await service.export_to_csv(lot_id)

    if export_file is None or export_file.file_path is None:
        await callback.message.answer(LOT_NOT_FOUND)
        await callback.answer()
        return

    path = Path(export_file.file_path)
    await callback.message.answer(EXPORT_CREATED)
    await callback.message.answer_document(FSInputFile(path))
    await callback.answer()