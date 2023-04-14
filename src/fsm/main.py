from aiogram.dispatcher.filters.state import StatesGroup, State


class MainFSM(StatesGroup):
    url_from_start = State()
    main_menu = State()
    url = State()
    photo_list_page = State()
    photo_detail = State()
    photo_delete = State()
