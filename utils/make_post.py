from typing import List, Type

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType
from aiogram.types.chat import Chat
from aiogram.types import ParseMode
from utils.replies import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputMediaVideo, InputMediaPhoto, InputMedia
from create_bot import ADMINS, bot
from keyboards.admin_kb import main_kb, button3
import validators
from config import config
import typing as tp
from db.db import Users, Bans, engine, get_session


class FSMMakePost(StatesGroup):
    title = State()
    photo = State()
    video = State()
    link = State()
    link_title = State()


button1 = KeyboardButton("Отмена")
button2 = KeyboardButton("Отправить")

in_btn1 = InlineKeyboardButton("Текст", callback_data="title")
in_btn2 = InlineKeyboardButton("Фото", callback_data="photo")
in_btn3 = InlineKeyboardButton("Видео", callback_data="video")
in_btn4 = InlineKeyboardButton("Cсылка", callback_data="link")

title_kb = InlineKeyboardMarkup().add(in_btn2).add(in_btn3).add(in_btn4)
photo_kb = InlineKeyboardMarkup().add(in_btn1).add(in_btn3).add(in_btn4)
video_kb = InlineKeyboardMarkup().add(in_btn1).add(in_btn2).add(in_btn4)
link_kb = InlineKeyboardMarkup().add(in_btn1).add(in_btn2).add(in_btn3)

in_main_kb = InlineKeyboardMarkup().add(in_btn1).add(in_btn2).add(in_btn3).add(in_btn4)

edit_mod_kb = ReplyKeyboardMarkup(resize_keyboard=True)
edit_mod_kb.row(button1, button2)


def get_users():
    session = get_session(engine)
    users = session.query(Users).all()
    ban_users = session.query(Bans).all()
    ban_users = [user.id for user in ban_users]
    users = [user.id for user in users if user.id not in ban_users]
    return users


async def edit_mod(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = ""
        data["photos"] = []
        data["videos"] = []
        data["links"] = []
    await msg.reply(text="Вы в режиме публикации", reply_markup=edit_mod_kb, reply=False)
    await msg.reply(text="Добавить:", reply_markup=in_main_kb, reply=False)


async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.reply(text="Режим публикации выключен", reply_markup=main_kb, reply=False)


async def set_state_title(callback_query: types.CallbackQuery):
    await FSMMakePost.title.set()
    await bot.edit_message_text(text="Жду текст", chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id, reply_markup=title_kb)


async def set_state_photo(callback_query: types.CallbackQuery):
    await FSMMakePost.photo.set()
    await bot.edit_message_text(text="Жду фото", chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id, reply_markup=photo_kb)


async def set_state_video(callback_query: types.CallbackQuery):
    await FSMMakePost.video.set()
    await bot.edit_message_text(text="Жду видео", chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id, reply_markup=video_kb)


async def set_state_link(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, text="Жду ссылку", reply_markup=video_kb)
    await FSMMakePost.link.set()


async def add_title(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = msg.text
    await msg.reply("Текст получил", reply_markup=title_kb)


async def add_photo(msg: types.Message, state: FSMContext):
    photo = msg.photo.pop().file_id
    async with state.proxy() as data:
        data["photos"].append(photo)
    await msg.reply("Фото получил. Можно загрузить еще", reply_markup=photo_kb)


async def add_video(msg: types.Message, state: FSMContext):
    video = msg.video.file_id
    async with state.proxy() as data:
        data["photos"].append(video)
    await msg.reply("Видео получил. Можно загрузить еще", reply_markup=video_kb)


async def add_link(msg: types.Message, state: FSMContext):
    link = msg.text
    if not validators.url(link):
        await msg.reply("Некорректная ссылка", reply_markup=link_kb)
    else:
        async with state.proxy() as data:
            data["links"].append({"link": link})
        await msg.reply("Ссылку получил", reply_markup=link_kb)
        await FSMMakePost.link_title.set()
        await msg.reply("Жду название ссылки")


async def add_link_title(msg: types.Message, state: FSMContext):
    title = msg.text
    async with state.proxy() as data:
        data["links"][-1]["title"] = title
    await FSMMakePost.link.set()
    await msg.reply("Ссылка сформирована. Можно добавить еще!", reply_markup=link_kb)


async def post_sender(session, chat_id, text, videos, photos, links):
    if videos or photos:
        if len(videos) + len(photos) == 1:
            if videos:
                bot_msg = await bot.send_video(chat_id=chat_id, video=videos[0], caption=text)
                print(bot_msg.message_id)
            if photos:
                bot_msg = await bot.send_photo(chat_id=chat_id, photo=photos[0], caption=text)
                print(bot_msg.message_id)
        elif len(videos) + len(photos) > 1:
            media = []
            for video in videos:
                media.append(InputMedia(InputMediaVideo(video)))
            for photo in photos:
                media.append(InputMediaPhoto(photo))
            media[0]["caption"] = text
            bot_msg = await bot.send_media_group(chat_id=chat_id, media=media)
    if links:
        links_kb = InlineKeyboardMarkup()
        for link in links:
            title = link["title"]
            link = link["link"]
            links_kb.add(InlineKeyboardButton(text=title, url=link))
        links_msg = await bot.send_message(chat_id=chat_id, text="Прикрепленные ссылки:", reply_markup=links_kb)


async def send_post(msg: types.Message, state: FSMContext):
    session = get_session(engine)
    async with state.proxy() as data:
        text = data["title"] if data["title"] else ""
        videos = list(set(data["videos"]))
        photos = list(set(data["photos"]))
        links = data["links"]
    if len(photos)+len(videos) > 10:
        await msg.reply(text="Будут отправлены первые 10 медиа ⚠️", reply=False)
    if not text and not videos and not photos:
        await msg.reply(text="Мало информации", reply_markup=in_main_kb, reply=False)
    else:
        await state.finish()
        await post_sender(chat_id=2044572933, text=text, videos=videos, photos=photos, links=links)
        await msg.reply(text="Пост отправлен", reply_markup=main_kb, reply=False)


def register_handlers_make_posts(dp: Dispatcher):
    dp.register_message_handler(edit_mod, lambda msg: msg["from"]["id"] in ADMINS and msg.text == button3.text,
                                state="*")

    dp.register_message_handler(cancel, lambda msg: msg["from"]["id"] in ADMINS and msg.text == button1.text, state="*")

    dp.register_message_handler(send_post, lambda msg: msg["from"]["id"] in ADMINS and msg.text == button2.text,
                                state="*")

    dp.register_callback_query_handler(set_state_title,
                                       lambda msg: msg["from"]["id"] in ADMINS and msg.data == in_btn1.callback_data,
                                       state="*")

    dp.register_callback_query_handler(set_state_photo,
                                       lambda msg: msg["from"]["id"] in ADMINS and msg.data == in_btn2.callback_data,
                                       state="*")

    dp.register_callback_query_handler(set_state_video,
                                       lambda msg: msg["from"]["id"] in ADMINS and msg.data == in_btn3.callback_data,
                                       state="*")

    dp.register_callback_query_handler(set_state_link,
                                       lambda msg: msg["from"]["id"] in ADMINS and msg.data == in_btn4.callback_data,
                                       state="*")

    dp.register_message_handler(add_title,
                                lambda msg: msg["from"]["id"] in ADMINS and msg.text,
                                state=FSMMakePost.title)

    dp.register_message_handler(add_photo, lambda msg: msg["from"]["id"] in ADMINS,
                                state=FSMMakePost.photo, content_types=["photo"])

    dp.register_message_handler(add_video, lambda msg: msg["from"]["id"] in ADMINS,
                                state=FSMMakePost.video, content_types=["video"])

    dp.register_message_handler(add_link, lambda msg: msg["from"]["id"] in ADMINS and msg.text,
                                state=FSMMakePost.link)

    dp.register_message_handler(add_link_title, lambda msg: msg["from"]["id"] in ADMINS and msg.text,
                                state=FSMMakePost.link_title)
