from aiogram.fsm.state import State, StatesGroup


class ShiftStates(StatesGroup):
    '''Состояние для смены водителя'''
    waiting_for_order = State()
