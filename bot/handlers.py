from aiogram import F, types # noqa
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

from dependencies import bot, dp # noqa
from database import TaxiDB

db = TaxiDB()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚖 Начать смену")],
        [KeyboardButton(text="🏁 Завершить смену")]
    ],
    resize_keyboard=True
)

# Состояния пользователей (временное хранилище)
user_state = {}  # {user_id: {'shift_active': bool, 'shift_start': time, 'last_trip_time': time}} # noqa


@dp.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        "🚖 Привет! Это TaxiEarningsBot\n\n"
        "Я буду считать твой доход в реальном времени.\n"
        "Просто пиши сумму заказа после завершения поездки.",
        reply_markup=main_keyboard
    )


@dp.message(F.text == "🚖 Начать смену")
async def start_shift(message: Message):
    user_id = message.from_user.id
    user_state[user_id] = {
        'shift_active': True,
        'shift_start': datetime.now(),
        'last_trip_time': None
    }

    await message.answer(
        "✅ Смена начата!\n\n"
        "Теперь просто пиши сумму заказа после каждой поездки.",
        reply_markup=main_keyboard
    )


@dp.message(F.text.func(lambda text: text.replace('-', '').replace(' ', '').isdigit())) # noqa
async def process_trip(message: Message):
    user_id = message.from_user.id

    # Проверяем, активна ли смена
    if user_id not in user_state or not user_state[user_id]['shift_active']:
        await message.answer("❌ Сначала начни смену (кнопка 'Начать смену')")
        return

    # Получаем сумму (очищаем от лишних символов)
    amount = int(message.text.replace('-', '').replace(' ', ''))

    # Сохраняем поездку
    db.start_trip(amount, user_id)

    # Если это не первая поездка, считаем время с прошлой
    last_time = user_state[user_id]['last_trip_time']
    now = datetime.now()

    duration = None
    hourly_rate = None
    if last_time:
        duration = (now - last_time).total_seconds() / 60
        hourly_rate = int((amount / duration) * 60) if duration > 0 else 0

    # Обновляем время последней поездки
    user_state[user_id]['last_trip_time'] = now

    # Получаем статистику за смену
    stats = db.get_shift_stats(user_id)
    total = stats[1] or 0

    # Формируем ответ
    response = f"✅ Записал: {amount} руб"
    if duration and hourly_rate:
        response += f"\n🕒 Время: {duration:.1f} мин\n📊 Доход в час: {hourly_rate} руб/ч" # noqa
    response += f"\n📈 Всего за смену: {total} руб"

    await message.answer(response)


@dp.message(F.text == "🏁 Завершить смену")
async def end_shift(message: Message):
    user_id = message.from_user.id

    if user_id not in user_state or not user_state[user_id]['shift_active']:
        await message.answer("❌ Смена ещё не начата")
        return

    # Получаем статистику
    stats = db.get_shift_stats(user_id)
    trips_count, total, first, last = stats

    if first and last:
        # first и last - это строки с датами, конвертируем
        first_time = datetime.fromisoformat(first.replace(' ', 'T'))
        last_time = datetime.fromisoformat(last.replace(' ', 'T'))
        hours = (last_time - first_time).total_seconds() / 3600
        avg_hourly = int(total / hours) if hours > 0 else 0
    else:
        hours = 0
        avg_hourly = 0

    # Очищаем состояние
    del user_state[user_id]

    await message.answer(
        f"🏁 Смена завершена!\n\n"
        f"🚖 Заказов: {trips_count}\n"
        f"💰 Итого: {total} руб\n"
        f"⏱ Время: {hours:.1f} ч\n"
        f"📊 Средний час: {avg_hourly} руб/ч\n\n"
        f"🌙 Хорошего отдыха!",
        reply_markup=main_keyboard
    )
