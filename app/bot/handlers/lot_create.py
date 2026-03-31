from datetime import datetime
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import cancel_keyboard, confirm_lot_keyboard
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
    lot_repository = LotRepository(session)
    carrier_match_repository = CarrierMatchRepository(session)
    matching_service = MatchingService()
    provider = MockAtiSuProvider()

    return SearchService(
        lot_repository=lot_repository,
        carrier_match_repository=carrier_match_repository,
        matching_service=matching_service,
        provider=provider,
    )


def _text_or_empty(message: Message) -> str | None:
    if message.text is None:
        return None
    text = message.text.strip()
    return text or None


@router.message(F.text == "/lot")
async def cmd_lot(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LotCreationStates.route_from)
    await message.answer(ASK_ROUTE_FROM, reply_markup=cancel_keyboard())


@router.callback_query(F.data == "lot:create")
async def cb_create_lot(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LotCreationStates.route_from)
    await callback.message.answer(ASK_ROUTE_FROM, reply_markup=cancel_keyboard())
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
    await message.answer(ASK_ROUTE_TO, reply_markup=cancel_keyboard())


@router.message(LotCreationStates.route_to)
async def process_route_to(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    await state.update_data(route_to=text)
    await state.set_state(LotCreationStates.distance_km)
    await message.answer(ASK_DISTANCE, reply_markup=cancel_keyboard())


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

    await state.update_data(distance_km=distance_km)
    await state.set_state(LotCreationStates.deadline_at)
    await message.answer(ASK_DEADLINE, reply_markup=cancel_keyboard())


@router.message(LotCreationStates.deadline_at)
async def process_deadline(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    try:
        deadline_at = datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(INVALID_DATETIME)
        return

    await state.update_data(deadline_at=deadline_at.isoformat())
    await state.set_state(LotCreationStates.vehicle_type)
    await message.answer(ASK_VEHICLE_TYPE, reply_markup=cancel_keyboard())


@router.message(LotCreationStates.vehicle_type)
async def process_vehicle_type(message: Message, state: FSMContext) -> None:
    text = _text_or_empty(message)
    if text is None:
        await message.answer(EMPTY_VALUE)
        return

    await state.update_data(vehicle_type=text)
    await state.set_state(LotCreationStates.weight_tons)
    await message.answer(ASK_WEIGHT, reply_markup=cancel_keyboard())


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

    await state.update_data(weight_tons=str(weight_tons))
    await state.set_state(LotCreationStates.volume_m3)
    await message.answer(ASK_VOLUME, reply_markup=cancel_keyboard())


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

    volume_m3 = None if volume == 0 else str(volume)

    await state.update_data(volume_m3=volume_m3)
    await state.set_state(LotCreationStates.budget_rub)
    await message.answer(ASK_BUDGET, reply_markup=cancel_keyboard())


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

    await state.update_data(budget_rub=str(budget_rub))
    data = await state.get_data()

    summary = (
        "Проверь данные лота:\n\n"
        f"Откуда: {data['route_from']}\n"
        f"Куда: {data['route_to']}\n"
        f"Км: {data['distance_km']}\n"
        f"Дедлайн: {data['deadline_at']}\n"
        f"Тип ТС: {data['vehicle_type']}\n"
        f"Вес: {data['weight_tons']} т\n"
        f"Объём: {data['volume_m3'] or '-'} м³\n"
        f"Бюджет: {budget_rub} ₽"
    )

    await state.set_state(LotCreationStates.confirm)
    await message.answer(summary, reply_markup=confirm_lot_keyboard())


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

    await callback.message.answer(f"Лот #{lot.id} сохранён. Ищу перевозчиков...")
    await callback.answer()

    if not matches:
        await callback.message.answer(NO_MATCHES_FOUND)
        return

    text = _format_matches(LotRead.model_validate(lot), matches)
    markup = matches_with_export_keyboard(lot.id, [item.id for item in matches])
    await callback.message.answer(text, reply_markup=markup)


def _format_matches(lot: LotRead, matches) -> str:
    lines = [
        f"Лот #{lot.id}",
        f"Маршрут: {lot.route_from} -> {lot.route_to}",
        f"Тип ТС: {lot.vehicle_type}",
        f"Бюджет: {lot.budget_rub} ₽",
        "",
        "Найденные варианты:",
        "",
    ]

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