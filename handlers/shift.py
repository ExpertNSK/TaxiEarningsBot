import logging
import time

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core import dp, get_main_keyboard, get_shift_keyboard
from states import ShiftStates

logger = logging.getLogger(__name__)

# Коэффициент пересчета (грязные -> чистые)
# 383 руб → 291.75 руб = 76.1% (подставь свой)
NET_MULTIPLIER = 0.761


@dp.message(F.text == '🚕 Начать смену')
@dp.message(Command('work'))
async def cmd_work(message: Message, state: FSMContext):
    '''Начало смены'''
    await state.update_data(
        orders=[],
        total_net=0.0,
        shift_start=time.time()
    )
    await state.set_state(ShiftStates.waiting_for_order)
    await message.answer(
        '🚕 Смена начата! Присылай суммы заказов цифрами\n'
        'Чаевые отправляй так: 100*',
        reply_markup=get_shift_keyboard()
    )
    logger.info(f'Пользователь {message.from_user.id} начал смену')


@dp.message(F.text == '🏁 Завершить смену')
@dp.message(Command('stop'))
async def cmd_stop(message: Message, state: FSMContext):
    '''Завершение смены'''
    data = await state.get_data()
    orders = data.get('orders', [])
    total_net = data.get('total_net', 0.0)
    shift_start = data.get('shift_start')

    if not orders:
        await message.answer(
            'Смена не была начата. Нажми кнопку чтобы начать!',
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    time_worked = time.time() - shift_start
    hours = int(time_worked // 3600)
    minutes = int((time_worked % 3600) // 60)

    avg_hourly = (total_net / time_worked) * 3600 if time_worked > 0 else 0

    if hours > 0:
        time_str = f'{hours} ч {minutes} мин'
    else:
        time_str = f'{minutes} мин'

    await message.answer(
        f'🏁 *Смена завершена!*\n\n'
        f'⏱ Проработано: {time_str}\n'
        f'💰 Заработано: {total_net:.0f} руб\n'
        f'📊 Средний доход: {avg_hourly:.0f} руб/час\n'
        f'📦 Заказов: {len(orders)}',
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

    await state.clear()
    logger.info(f'Пользователь {message.from_user.id} завершил смену. '
                f'Итого: {total_net} руб')


@dp.message(ShiftStates.waiting_for_order, F.text.regexp(r'^\d+\*$|^\d+$'))
async def handle_order(message: Message, state: FSMContext):
    '''Обработка заказов и чаевых'''
    text = message.text
    current_time = time.time()

    # ЧАЕВЫЕ: формат "100*"
    if text.endswith('*'):
        tips = int(text[:-1])

        data = await state.get_data()
        orders = data.get('orders', [])

        if not orders:
            await message.answer('Сначала нужно сделать заказ!')
            return

        # Добавляем чаевые к последнему заказу
        last_time, last_net = orders[-1]
        new_net = last_net + tips  # чаевые без комиссии
        orders[-1] = (last_time, new_net)

        # Пересчитываем общую сумму
        total_net = sum(net for _, net in orders)
        await state.update_data(orders=orders, total_net=total_net)

        await message.answer(f'✅ Чаевые {tips} руб добавлены '
                             'к последнему заказу')
        logger.info(f'Чаевые {tips} руб от {message.from_user.id}')
        return

    # ЗАКАЗ: обычная сумма
    amount_gross = int(text)
    amount_net = amount_gross * NET_MULTIPLIER

    data = await state.get_data()
    orders = data.get('orders', [])
    total_net = data.get('total_net', 0.0)
    shift_start = data.get('shift_start', current_time)

    response = f'✅ Заказ: {amount_gross} руб\n'

    # Доходность на отрезке
    if orders:
        prev_time, prev_net = orders[-1]
        time_diff = current_time - prev_time
        minutes = int(time_diff // 60)
        seconds = int(time_diff % 60)
        time_str = f'{minutes:02d}:{seconds:02d}'

        if time_diff > 0:
            segment_hourly = (amount_net / time_diff) * 3600
            response += (f'🕒 Доходность на отрезке({time_str}): '
                         f'{segment_hourly:.0f} руб/час\n')

    # Сохраняем заказ
    orders.append((current_time, amount_net))
    total_net += amount_net
    await state.update_data(orders=orders, total_net=total_net)

    # Общее время работы
    time_worked = current_time - shift_start
    worked_minutes = int(time_worked // 60)
    worked_seconds = int(time_worked % 60)
    worked_str = f'{worked_minutes:02d}:{worked_seconds:02d}'

    if time_worked > 0:
        avg_hourly = (total_net / time_worked) * 3600
        response += f'📊 Доходность за смену: {avg_hourly:.0f} руб/час\n'

    # Прогноз
    forecast = avg_hourly * 12
    response += f'🔮 Прогноз за 12ч: {forecast:.0f} руб\n'

    response += f'📈 Всего(за {worked_str}) {total_net:.0f} руб'

    await message.answer(response, reply_markup=get_shift_keyboard())
    logger.info(f'Заказ {amount_gross} руб (чистыми {amount_net:.0f}) '
                f'от {message.from_user.id}')
