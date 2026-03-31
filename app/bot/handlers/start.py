from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.common import start_keyboard
from app.bot.texts.messages import HELP_LOT_TEXT, START_TEXT

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    await message.answer(
        START_TEXT,
        reply_markup=start_keyboard(),
    )


@router.message(F.text == "/help")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_LOT_TEXT)


@router.callback_query(F.data == "lot:create")
async def start_from_button(callback: CallbackQuery) -> None:
    await callback.message.answer(HELP_LOT_TEXT)
    await callback.answer()