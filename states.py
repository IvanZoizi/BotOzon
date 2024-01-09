from aiogram.dispatcher.filters.state import StatesGroup, State


class UrlStates(StatesGroup):
    url = State()