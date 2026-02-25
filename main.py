import asyncio
import logging

from core import bot, dp
from handlers import shift, start  # noqa

logger = logging.getLogger(__name__)


async def main():
    logger.info('Запускаем бота')
    try:
        await dp.start_polling(
            bot,
            skip_updates=True
        )
    except KeyboardInterrupt:
        logger.info('Бот остановлен пользователем')
    except Exception as e:
        logger.error(f'Ошибка при работе бота: {e}', exc_info=True)
    finally:
        logger.info('Завершение работы')


if __name__ == '__main__':
    asyncio.run(main())
