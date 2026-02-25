import asyncio
from dependencies import bot, dp
import handlers  # это загружает хендлеры


async def main():
    print("🚖 TaxiEarningsBot запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
