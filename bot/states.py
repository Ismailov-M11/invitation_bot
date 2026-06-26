from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    waiting_password = State()


class GuestState(StatesGroup):
    waiting_name_uz = State()
    waiting_name_ru = State()
