from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Создать лот", callback_data="lot:create")
    builder.adjust(1)
    return builder.as_markup()


def confirm_lot_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="lot:confirm")
    builder.button(text="❌ Отмена", callback_data="lot:cancel")
    builder.adjust(2)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="lot:cancel")
    builder.adjust(1)
    return builder.as_markup()


def vehicle_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Реф", callback_data="vehicle:реф")
    builder.button(text="Тент", callback_data="vehicle:тент")
    builder.button(text="Фура", callback_data="vehicle:фура")
    builder.button(text="❌ Отмена", callback_data="lot:cancel")
    builder.adjust(3, 1)
    return builder.as_markup()


def skip_volume_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пропустить", callback_data="lot:skip_volume")
    builder.button(text="❌ Отмена", callback_data="lot:cancel")
    builder.adjust(1)
    return builder.as_markup()