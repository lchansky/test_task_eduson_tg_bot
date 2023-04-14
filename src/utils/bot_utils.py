from bot import bot
from db.models import Photo
from utils import text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import DEFAULT_PAGE_SIZE


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup(row_width=1)
    inline_markup.add(
        InlineKeyboardButton(text.add_new_photos_button, callback_data='add_new_photos'),
        InlineKeyboardButton(text.photo_list_button, callback_data='photo_list'),
        InlineKeyboardButton(text.download_table_button, callback_data='download_table'),
    )
    return inline_markup


def add_photos_buttons(photos: list[Photo], inline_markup: InlineKeyboardMarkup):
    for photo in photos:
        inline_markup.add(
            InlineKeyboardButton(f'{photo.author} ({photo.picsum_id})', callback_data=f'photo_detail:{photo.id}')
        )


def add_page_buttons(inline_markup: InlineKeyboardMarkup, photos_count: int, page: int):
    if photos_count > DEFAULT_PAGE_SIZE:
        pages_count = (photos_count - 1) // DEFAULT_PAGE_SIZE + 1
        page_buttons = []
        if page > 1:
            page_buttons.append(InlineKeyboardButton(f'⬅️️ Страница {page - 1}', callback_data='prev_page'))
        if page < pages_count:
            page_buttons.append(InlineKeyboardButton(f'➡️ Страница {page + 1}', callback_data='next_page'))
        inline_markup.add(*page_buttons)


async def send_main_menu(chat_id: int) -> Message:
    inline_markup = get_main_menu_keyboard()
    return await bot.send_message(chat_id, text.main_menu, reply_markup=inline_markup)


def change_page(current_page: int, pages_count: int, next_or_prev: str) -> int:
    if next_or_prev == 'prev_page':
        page = current_page - 1
    elif next_or_prev == 'next_page':
        page = current_page + 1
    else:
        page = current_page

    if page < 1:
        page = 1
    if page > pages_count:
        page = pages_count

    return page


def create_csv_table_bytes(photos: list[Photo]) -> bytes:
    prepared_rows = (
        f'{photo.picsum_id},{photo.author},{photo.width},{photo.height},{photo.url},{photo.download_url}'
        for photo in photos
    )
    csv_rows = 'picsum_id,author,width,height,url,download_url\n'
    csv_rows += '\n'.join(prepared_rows)
    return csv_rows.encode('utf-8')
