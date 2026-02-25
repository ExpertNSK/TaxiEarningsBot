import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    load_dotenv()
    token = os.getenv('BOT_TOKEN')

    if not token:
        raise ValueError('Токен не найден в .env файлей')

    bot = Bot(token)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    logger.info('ENV, bot и dispatcher загружены.')
except ValueError as e:
    logger.error(f'Ошибка конфигурации: {e}')
    raise
except Exception as e:
    logger.error(f'Неизвестная ошибка при инициализации: {e}', exc_info=True)
    raise
