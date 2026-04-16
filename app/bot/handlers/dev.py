from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.atrucks.mock import MockAtrucksProvider
from app.repositories.lot import LotRepository
from app.services.lot_service import LotService

router = Router()


@router.message(F.text == "/mock_lot")
async def generate_mock_lot(message: Message, session: AsyncSession):
    provider = MockAtrucksProvider()
    lot_data = provider.generate_lot()

    service = LotService(LotRepository(session))
    lot = await service.create_lot(lot_data)

    await message.answer(f"Сгенерирован лот #{lot.id}")