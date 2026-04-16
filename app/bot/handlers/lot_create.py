from datetime import datetime
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import (
    cancel_keyboard,
    confirm_lot_keyboard,
    skip_volume_keyboard,
    vehicle_type_keyboard,
)
from app.bot.keyboards.matches import matches_with_export_keyboard
from app.bot.states.lot import LotCreationStates
from app.bot.texts.messages import (
    ASK_BUDGET,
    ASK_DEADLINE,
    ASK_DISTANCE,
    ASK_ROUTE_FROM,
    ASK_ROUTE_TO,
    ASK_VEHICLE_TYPE,
    ASK_VOLUME,
    ASK_WEIGHT,
    EMPTY_VALUE,
    INVALID_DATETIME,
    INVALID_NUMBER,
    LOT_CANCELLED,
    LOT_SAVED_TEXT,
    LOT_SUMMARY_TITLE,
    MATCHES_TITLE,
    NO_MATCHES_FOUND,
)
from app.domain.schemas.lot import LotCreate, LotRead
from app.integrations.ati_su.mock import MockAtiSuProvider
from app.repositories.carrier_match import CarrierMatchRepository
from app.repositories.lot import LotRepository
from app.services.lot_service import LotService
from app.services.matching_service import MatchingService
from app.services.search_service import SearchService

router = Router()


async def _build_search_service(session: AsyncSession) -> SearchService:
    return SearchService(
        lot_repository=LotRepository(session),
        carrier_match_repository=CarrierMatchRepository(session),
        matching_service=MatchingService(),
        provider=MockAtiSuProvider(),
    )


def _text_or_empty(message: Message) -> str | None:
    if message.text is None:
        return None
    text = message.text.strip()
    return text or None


def _parse_deadline(text: str) -> datetime | None:
    text = text.strip()

    formats_with_year = [
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d %H:%M",
        "%d.%m.%Y %H:%M",
        "%d-%m-%Y %H:%M",
    ]
    formats_without_year = [
        "%d.%m %H:%M",
        "%d-%m %H:%M",
        "%d/%m %H:%M",
    ]

    for fmt in formats_with_year:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    now = datetime.now()
    for fmt in formats_without_year:
        try:
            partial = datetime.strptime(text, fmt)
            candidate = partial.replace(year=now.year)
            if candidate < now:
                candidate = candidate.replace(year=now.year + 1)
            return candidate
        except ValueError:
            pass

    return None


def _format_lot_summary(data: dict) -> str:
    volume_text = f"{data['volume_m3']} м³" if data["volume_m3"] is not None else "не указан"

    return (
        f"{LOT_SUMMARY_TITLE}\n\n"
        f"📍 *Откуда:* {data['route_from']}\n"
        f"📍 *Куда:* {data['route_to']}\n"
        f"🛣 *Расстояние:* {data['distance_km']} км\n"
        f"📅 *Дедлайн:* {data['deadline_at']}\n"
        f"🚚 *Тип ТС:* {data['vehicle_type']}\n"
        f"⚖️ *Вес:* {data['weight_tons']} т\n"
        f"📦 *Объём:* {volume_text}\n"
        f"💰 *Бюджет:* {data['budget_rub']} ₽"
    )


def _format_matches(lot: LotRead, matches) -> str:
    lines = [
        f"🚛 *Лот #{lot.id}*",
        f"📍 {lot.route_from} → {lot.route_to}",
        f"🚚 Тип ТС: {lot.vehicle_type}",
        f"💰 Бюджет: {lot.budget_rub} ₽",
        "",
        MATCHES_TITLE,
        "",
    ]

    for index, match in enumerate(matches, start=1):
        contact = match.contact_phone or match.contact_nick or "-"
        rating = match.rating or "-"
        lines.extend(
            [
                f"*{index}. {match.carrier_name}*",
                f"💵 Цена: {match.proposed_price} ₽",
                f"⭐ Рейтинг: {rating}",
                f"📞 Контакт: {contact}",
                f"📊 Score: {match.score}",
                "",
            ]
        )

    return "\n".join(lines).strip()


@router.message(F.text == "/lot")
async def cmd_lot(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LotCreationStates.route_from)
    await message.answer(ASK_ROUTE_FROM, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "lot:create")
async def cb_create_lot(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LotCreationStates.route_from)
    await callback.message.answer(ASK_ROUTE_FROM, reply_markup=cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "lot:cancel")
async def cb_cancel_lot(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(LOT_CANCELLED)
    await callback.answer()


@router.message(LotCreationStates.route_from)
async def process_route_from(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    await state.update_data(route_from=text)
    await state.set_state(LotCreationStates.route_to)
    await message.answer(ASK_ROUTE_TO, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.message(LotCreationStates.route_to)
async def process_route_to(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    await state.update_data(route_to=text)
    await state.set_state(LotCreationStates.distance_km)
    await message.answer(ASK_DISTANCE, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.message(LotCreationStates.distance_km)
async def process_distance(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    try:
        distance_km = int(text)
    except ValueError:
        await message.answer(INVALID_NUMBER)
        return

    if distance_km <= 0:
        await message.answer(INVALID_NUMBER)
        return

    await state.update_data(distance_km=distance_km)
    await state.set_state(LotCreationStates.deadline_at)
    await message.answer(ASK_DEADLINE, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.message(LotCreationStates.deadline_at)
async def process_deadline(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    deadline_at = _parse_deadline(text)
    if deadline_at is None:
        await message.answer(INVALID_DATETIME, parse_mode="Markdown")
        return

    await state.update_data(deadline_at=deadline_at.isoformat())
    await state.set_state(LotCreationStates.vehicle_type)
    await message.answer(
        ASK_VEHICLE_TYPE,
        reply_markup=vehicle_type_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("vehicle:"))
async def cb_vehicle_type(callback: CallbackQuery, state: FSMContext) -> None:
    vehicle_type = callback.data.split(":", 1)[1]

    await state.update_data(vehicle_type=vehicle_type)
    await state.set_state(LotCreationStates.weight_tons)
    await callback.message.answer(ASK_WEIGHT, reply_markup=cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.message(LotCreationStates.vehicle_type)
async def process_vehicle_type_manual(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    await state.update_data(vehicle_type=text.lower())
    await state.set_state(LotCreationStates.weight_tons)
    await message.answer(ASK_WEIGHT, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.message(LotCreationStates.weight_tons)
async def process_weight(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    try:
        weight_tons = Decimal(text.replace(",", "."))
    except InvalidOperation:
        await message.answer(INVALID_NUMBER)
        return

    if weight_tons <= 0:
        await message.answer(INVALID_NUMBER)
        return

    await state.update_data(weight_tons=str(weight_tons))
    await state.set_state(LotCreationStates.volume_m3)
    await message.answer(
        ASK_VOLUME,
        reply_markup=skip_volume_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "lot:skip_volume")
async def cb_skip_volume(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(volume_m3=None)
    await state.set_state(LotCreationStates.budget_rub)
    await callback.message.answer(ASK_BUDGET, reply_markup=cancel_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.message(LotCreationStates.volume_m3)
async def process_volume(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    try:
        volume = Decimal(text.replace(",", "."))
    except InvalidOperation:
        await message.answer(INVALID_NUMBER)
        return

    if volume <= 0:
        await message.answer(INVALID_NUMBER)
        return

    await state.update_data(volume_m3=str(volume))
    await state.set_state(LotCreationStates.budget_rub)
    await message.answer(ASK_BUDGET, reply_markup=cancel_keyboard(), parse_mode="Markdown")


@router.message(LotCreationStates.budget_rub)
async def process_budget(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    try:
        budget_rub = Decimal(text.replace(",", "."))
    except InvalidOperation:
        await message.answer(INVALID_NUMBER)
        return

    if budget_rub <= 0:
        await message.answer(INVALID_NUMBER)
        return

    await state.update_data(budget_rub=str(budget_rub))
    data = await state.get_data()

    await state.set_state(LotCreationStates.confirm)
    await message.answer(
        _format_lot_summary(data),
        reply_markup=confirm_lot_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "lot:confirm")
async def cb_confirm_lot(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()

    payload = LotCreate(
        route_from=data["route_from"],
        route_to=data["route_to"],
        distance_km=data["distance_km"],
        deadline_at=datetime.fromisoformat(data["deadline_at"]),
        vehicle_type=data["vehicle_type"],
        weight_tons=Decimal(data["weight_tons"]),
        volume_m3=Decimal(data["volume_m3"]) if data["volume_m3"] is not None else None,
        budget_rub=Decimal(data["budget_rub"]),
        external_source="telegram",
        created_by=str(callback.from_user.id) if callback.from_user else None,
    )

    lot_service = LotService(LotRepository(session))
    lot = await lot_service.create_lot(payload)

    search_service = await _build_search_service(session)
    matches = await search_service.search_for_lot(lot.id, limit=5)

    await state.clear()

    await callback.message.answer(
        LOT_SAVED_TEXT.format(lot_id=lot.id),
        parse_mode="Markdown",
    )
    await callback.answer()

    if not matches:
        await callback.message.answer(NO_MATCHES_FOUND)
        return

    text = _format_matches(LotRead.model_validate(lot), matches)
    markup = matches_with_export_keyboard(lot.id, [item.id for item in matches])
    await callback.message.answer(text, reply_markup=markup, parse_mode="Markdown")