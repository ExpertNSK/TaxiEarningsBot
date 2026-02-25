import logging

from aiogram.filters import CommandStart
from aiogram.types import Message

from core import dp, get_main_keyboard

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def start_command(message: Message):
    try:
        await message.answer(
            '👋 Привет! Я бот для учёта смен в такси.\n'
            'Нажми кнопку чтобы начать работу!',
            reply_markup=get_main_keyboard()
        )
        logger.info('Команда старт, возвращаем приветствие')
    except Exception as e:
        logger.error(f'Неизвестная ошибка: {e}')
