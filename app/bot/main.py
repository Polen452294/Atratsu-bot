import asyncio

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject

from app.bot.handlers import lot_create_router, matches_router, my_lots_router, start_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


async def main() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start_router)
    dp.include_router(lot_create_router)
    dp.include_router(matches_router)
    dp.include_router(my_lots_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())