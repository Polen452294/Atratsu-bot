from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def lot_actions_keyboard(lot_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Показать варианты", callback_data=f"lot:matches:{lot_id}")
    builder.button(text="Экспорт JSON", callback_data=f"lot:export:json:{lot_id}")
    builder.button(text="Экспорт CSV", callback_data=f"lot:export:csv:{lot_id}")
    builder.adjust(1)
    return builder.as_markup()


def lot_list_keyboard(lot_ids: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for lot_id in lot_ids:
        builder.button(text=f"Лот #{lot_id}", callback_data=f"lot:open:{lot_id}")

    builder.adjust(1)
    return builder.as_markup()


def deal_actions_keyboard(deal_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Инициировать сделку", callback_data=f"deal:initiate:{deal_id}")
    builder.adjust(1)
    return builder.as_markup()