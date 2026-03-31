from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def matches_keyboard(match_ids: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for index, match_id in enumerate(match_ids, start=1):
        builder.button(
            text=f"Выбрать {index}",
            callback_data=f"match:select:{match_id}",
        )

    builder.button(text="Отмена", callback_data="lot:cancel")
    builder.adjust(1)
    return builder.as_markup()


def matches_with_export_keyboard(lot_id: int, match_ids: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for index, match_id in enumerate(match_ids, start=1):
        builder.button(
            text=f"Выбрать {index}",
            callback_data=f"match:select:{match_id}",
        )

    builder.button(text="Экспорт JSON", callback_data=f"lot:export:json:{lot_id}")
    builder.button(text="Экспорт CSV", callback_data=f"lot:export:csv:{lot_id}")
    builder.button(text="Отмена", callback_data="lot:cancel")
    builder.adjust(1)
    return builder.as_markup()