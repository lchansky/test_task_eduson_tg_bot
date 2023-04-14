from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DEFAULT_PAGE_SIZE
from db.models import Photo
from exceptions.validation import URLValidationError
from picsum.api import PicsumAPI
from utils import text
from utils.bot_utils import create_csv_table_bytes, change_page, add_photos_buttons, get_main_menu_keyboard, \
    add_page_buttons


def bot_utils():
    csv_header = 'picsum_id,author,width,height,url,download_url\n'
    photos = [
        Photo(id=1, picsum_id=10, author='Test', width=100, height=50, url='url', download_url='download_url')
    ]
    result = (csv_header + '10,Test,100,50,url,download_url').encode('utf-8')
    assert create_csv_table_bytes(photos) == result

    assert change_page(1, 5, 'next_page') == 2
    assert change_page(5, 5, 'next_page') == 5
    assert change_page(1, 5, 'prev_page') == 1
    assert change_page(2, 5, 'prev_page') == 1

    inline = InlineKeyboardMarkup()
    expected = InlineKeyboardMarkup()
    expected.add(InlineKeyboardButton(f'Test (10)', callback_data=f'photo_detail:1'))
    add_photos_buttons(photos, inline)
    assert inline == expected

    expected = InlineKeyboardMarkup()
    expected.add(InlineKeyboardButton(text.add_new_photos_button, callback_data='add_new_photos'))
    expected.add(InlineKeyboardButton(text.photo_list_button, callback_data='photo_list'))
    expected.add(InlineKeyboardButton(text.download_table_button, callback_data='download_table'))
    assert get_main_menu_keyboard() == expected

    count_photos = DEFAULT_PAGE_SIZE * 2 + 3
    result = InlineKeyboardMarkup()
    add_page_buttons(result, count_photos, 1)
    expected = InlineKeyboardMarkup()
    expected.add(InlineKeyboardButton(f'➡️ Страница 2', callback_data='next_page'))
    assert result == expected
    result = InlineKeyboardMarkup()
    add_page_buttons(result, count_photos, 2)
    expected = InlineKeyboardMarkup()
    expected.add(InlineKeyboardButton(f'⬅️️ Страница 1', callback_data='prev_page'))
    expected.add(InlineKeyboardButton(f'➡️ Страница 3', callback_data='next_page'))
    assert result == expected
    result = InlineKeyboardMarkup()
    add_page_buttons(result, count_photos, 3)
    expected = InlineKeyboardMarkup()
    expected.add(InlineKeyboardButton(f'⬅️️ Страница 2', callback_data='prev_page'))
    assert result == expected


def picsum_api():
    api = PicsumAPI()

    api.validate_url('https://picsum.photos/v2/list?page=5')
    api.validate_url('https://picsum.photos/v2/list?page=1')
    api.validate_url('https://picsum.photos/v2/list?lalala')

    try:
        api.validate_url('https://picum.photos/v2/list?page=5')
        assert False
    except URLValidationError:
        pass
    try:
        api.validate_url('photos/v2/list?page=1')
        assert False
    except URLValidationError:
        pass
    try:
        api.validate_url('wrong_url')
        assert False
    except URLValidationError:
        pass


def run_tests():
    bot_utils()
    picsum_api()
    print('✅ Tests passed')
