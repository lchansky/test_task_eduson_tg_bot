import io

from aiogram import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ChatType, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.utils.exceptions import BadRequest

from config import DEFAULT_PAGE_SIZE
from db.db_manager import DBManager
from exceptions.validation import URLValidationError
from fsm.main import MainFSM
from picsum.api import PicsumAPI
from utils import text, bot_utils
from utils.text import get_back_button


db = DBManager()
api = PicsumAPI()


async def start(message: Message, state: FSMContext):
    await message.answer(text.onboarding_message, disable_web_page_preview=True)
    await state.set_state(state=MainFSM.url_from_start.state)


async def url_received_from_start(message: Message, state: FSMContext):
    url = message.text
    try:
        photos = api.request_photos(url)
    except ConnectionError:
        await message.answer(text.picsum_is_unavailable)
        await state.set_state(MainFSM.main_menu.state)
        await bot_utils.send_main_menu(message.chat.id)
        return
    except URLValidationError:
        await message.answer(text.url_not_correct_then_send_menu)
        await state.set_state(MainFSM.main_menu.state)
        await bot_utils.send_main_menu(message.chat.id)
        return

    db.add_photos(message.from_id, photos)
    await message.answer(text.photos_saved)
    await state.set_state(MainFSM.main_menu.state)
    await bot_utils.send_main_menu(message.chat.id)


async def add_new_photos(callback_query: CallbackQuery, state: FSMContext):
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton(get_back_button, callback_data='main_menu'))
    await callback_query.message.edit_text(
        text.request_url_message,
        reply_markup=inline_markup,
        disable_web_page_preview=True,
    )
    await callback_query.answer()
    await state.set_state(state=MainFSM.url.state)


async def url_received(message: Message, state: FSMContext):
    url = message.text
    try:
        photos = api.request_photos(url)
    except ConnectionError:
        await message.answer(text.picsum_is_unavailable)
        await state.set_state(MainFSM.main_menu.state)
        await bot_utils.send_main_menu(message.chat.id)
        return
    except URLValidationError:
        inline_markup = InlineKeyboardMarkup()
        inline_markup.add(InlineKeyboardButton(get_back_button, callback_data='main_menu'))
        await message.answer(text.url_not_correct_try_again, reply_markup=inline_markup)
        return

    db.add_photos(message.from_id, photos)
    await message.answer(text.photos_saved)
    await state.set_state(MainFSM.main_menu.state)
    await bot_utils.send_main_menu(message.chat.id)


async def photo_list(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(MainFSM.photo_list_page.state)
    inline_markup = InlineKeyboardMarkup()

    photos_count = db.get_photos_count(callback_query.from_user.id)

    message_text = text.photo_list
    if photos_count == 0:
        message_text += '\n' + text.empty_page
        try:
            await callback_query.message.edit_text(message_text, reply_markup=inline_markup)
        except BadRequest:
            await callback_query.message.answer(message_text, reply_markup=inline_markup)
        await state.set_state(MainFSM.main_menu.state)
        await bot_utils.send_main_menu(callback_query.message.chat.id)
        return

    adv_data = await state.get_data()
    page = adv_data.get('photo_list_page', 1)

    pages_count = (photos_count - 1) // DEFAULT_PAGE_SIZE + 1

    page = bot_utils.change_page(page, pages_count, next_or_prev=callback_query.data)
    await state.update_data(photo_list_page=page)

    photos = db.get_photos(
        callback_query.from_user.id,
        offset=DEFAULT_PAGE_SIZE * (page - 1),
        limit=DEFAULT_PAGE_SIZE,
    )

    bot_utils.add_photos_buttons(photos, inline_markup)
    bot_utils.add_page_buttons(inline_markup, photos_count, page)
    inline_markup.add(InlineKeyboardButton(text.main_menu_button, callback_data='main_menu'))

    try:
        await callback_query.message.edit_text(message_text, reply_markup=inline_markup)
    except BadRequest:
        await callback_query.message.answer(message_text, reply_markup=inline_markup)


async def photo_detail(callback_query: CallbackQuery, state: FSMContext):
    photo_id = int(callback_query.data.split(':')[1])
    photo = db.get_photo(photo_id=photo_id)

    await state.set_state(MainFSM.photo_detail.state)

    try:
        picsum_photo = api.request_photo_info(photo_id=photo.picsum_id)
        picsum_photo_bytes = api.request_photo_bytes(url=picsum_photo.get('download_url'))
    except ConnectionError:
        await callback_query.message.answer(text.picsum_is_unavailable)
        await state.set_state(MainFSM.main_menu.state)
        await bot_utils.send_main_menu(callback_query.message.chat.id)
        return

    stream = io.BytesIO(picsum_photo_bytes)
    input_file = InputFile(stream)

    message_text = text.photo_description_template.format(
        author=picsum_photo.get('author'),
        id=picsum_photo.get('id'),
        width=picsum_photo.get('width'),
        height=picsum_photo.get('height'),
        url=picsum_photo.get('url'),
        download_url=picsum_photo.get('download_url'),
    )

    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton(text.delete_button, callback_data=f'delete_photo:{photo_id}'))
    inline_markup.add(InlineKeyboardButton(text.get_back_button, callback_data=f'photo_list'))

    await callback_query.message.answer_photo(input_file, message_text, reply_markup=inline_markup)


async def delete_photo(callback_query: CallbackQuery, state: FSMContext):
    photo_id = int(callback_query.data.split(':')[1])
    photo = db.get_photo(photo_id=photo_id)

    await state.set_state(MainFSM.photo_delete.state)

    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton(text.yes_button, callback_data=f'delete_photo_confirmed:{photo_id}'))
    inline_markup.add(InlineKeyboardButton(text.no_button, callback_data=f'photo_list'))

    message_text = text.photo_delete_confirmation_template.format(
        author=photo.author,
        id=photo.picsum_id,
    )
    await callback_query.message.edit_caption(message_text, reply_markup=inline_markup)


async def delete_photo_confirmed(callback_query: CallbackQuery, state: FSMContext):
    photo_id = int(callback_query.data.split(':')[1])
    db.delete_photo(photo_id=photo_id)

    await state.set_state(MainFSM.photo_list_page.state)
    await callback_query.message.edit_caption(text.photo_deleted_successfully)

    await photo_list(callback_query, state)


async def main_menu_from_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.set_state(MainFSM.main_menu.state)
    await callback_query.answer()
    await bot_utils.send_main_menu(callback_query.message.chat.id)


async def main_menu_from_command(message: Message, state: FSMContext):
    await state.reset_state()
    await state.set_state(MainFSM.main_menu.state)
    await bot_utils.send_main_menu(message.chat.id)


async def get_photos_table(callback_query: CallbackQuery, state: FSMContext):
    photos = db.get_photos(user_tg_id=callback_query.from_user.id)
    file_bytes = bot_utils.create_csv_table_bytes(photos)
    await callback_query.answer('Таблица начала генерироваться...')
    await callback_query.message.answer_document(
        document=('table.csv', file_bytes),
        caption=text.spreadsheet_created,
    )


def register_handlers(dp: Dispatcher):
    private_message = ChatTypeFilter(chat_type=ChatType.PRIVATE)

    dp.register_message_handler(start, private_message, commands=['start'], state='*')
    dp.register_message_handler(url_received_from_start, private_message, state=MainFSM.url_from_start)

    dp.register_message_handler(main_menu_from_command, private_message, commands=['menu'], state='*')
    dp.register_callback_query_handler(main_menu_from_callback, private_message, lambda callback_query: callback_query.data == 'main_menu', state='*')

    dp.register_callback_query_handler(add_new_photos, private_message, lambda callback_query: callback_query.data == 'add_new_photos', state='*')
    dp.register_message_handler(url_received, private_message, state=MainFSM.url)

    dp.register_callback_query_handler(photo_list, private_message, lambda callback_query: callback_query.data == 'photo_list', state='*')
    dp.register_callback_query_handler(photo_list, private_message, lambda callback_query: callback_query.data in ('next_page', 'prev_page'), state=MainFSM.photo_list_page)

    dp.register_callback_query_handler(photo_detail, private_message, lambda callback_query: callback_query.data.startswith('photo_detail:'), state='*')

    dp.register_callback_query_handler(delete_photo, private_message, lambda callback_query: callback_query.data.startswith('delete_photo:'), state=MainFSM.photo_detail)
    dp.register_callback_query_handler(delete_photo_confirmed, private_message, lambda callback_query: callback_query.data.startswith('delete_photo_confirmed:'), state=MainFSM.photo_delete)

    dp.register_callback_query_handler(get_photos_table, private_message, lambda callback_query: callback_query.data == 'download_table', state='*')
