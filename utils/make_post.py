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
callback_data = [i[0].callback_data for i in in_main_kb["inline_keyboard"]]

edit_mod_kb = ReplyKeyboardMarkup(resize_keyboard=True)
edit_mod_kb.row(button1, button2)

test_id = "AgACAgIAAxkBAAIE_WFwPsU5q-hKretiDX3T9mwW_PnqAAIEtzEbn5GASwXjo_gexnX0AQADAgADcwADIAQ"
post = {}


async def edit_mod(msg: types.Message):
    post["title"] = ""
    post["photos"] = []
    post["videos"] = []
    post["links"] = []
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
    await bot.edit_message_text(text="Жду видео", chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=video_kb)


async def set_state_link(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, text="Жду ссылку", reply_markup=video_kb)
    await FSMMakePost.link.set()


async def add_title(msg: types.Message):
    post["title"] = msg.text
    await msg.reply("Текст получил", reply_markup=title_kb)


async def add_photo(msg: types.Message):
    photo = msg.photo.pop().file_id
    post["photos"].append(photo)
    await msg.reply("Фото получил. Можно загрузить еще", reply_markup=photo_kb)


async def add_video(msg: types.Message):
    video = msg.video.file_id
    post["videos"].append(video)
    await msg.reply("Видео получил. Можно загрузить еще", reply_markup=video_kb)


async def add_link(msg: types.Message):
    link = msg.text
    if not validators.url(link):
        await msg.reply("Некорректная ссылка", reply_markup=link_kb)
    else:
        post["links"].append({"link": link})
        await msg.reply("Ссылку получил", reply_markup=link_kb)
        await FSMMakePost.link_title.set()
        await msg.reply("Жду название ссылки")


async def pin_links(msg: types.Message):
    Chat = await bot.send_message(chat_id=msg.from_user.id, text="12323")
    print(Chat)


async def view_post(post, chat_id):
    text = post["title"] if post["title"] else None
    videos = list(set(post["videos"]))
    photos = list(set(post["photos"]))
    print((photos))
    links = post["links"]
    inline_kb = InlineKeyboardMarkup()
    if links:
        for link in links:
            btn = InlineKeyboardButton(text=link["title"], url=link["link"])
            inline_kb.add(btn)
    if videos or photos:
        if len(videos) + len(photos) == 1:
            if videos:
                await bot.send_video(chat_id=chat_id, video=videos[0], caption=text, reply_markup=inline_kb)
            if photos:
                print(photos)
                print(photos[0])
                await bot.send_photo(chat_id=chat_id, photo=photos[0], caption=text, reply_markup=inline_kb)
        elif len(videos) + len(photos) > 1:
            media = []
            for video in videos:
                media.append(InputMedia(InputMediaVideo(video)))
            for photo in photos:
                media.append(InputMediaPhoto(photo))
            media[0]["caption"]=text
            msg_post = await bot.send_media_group(chat_id=chat_id, media=media)
            msg_link = await bot.send_message(chat_id=chat_id, text="Прикрепленные ссылки:", reply_markup=inline_kb)
            # await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg[0].message_id, reply_markup=inline_kb)
            # await msg_post[0].reply("Ссылка")


async def add_link_title(msg: types.Message):
    title = msg.text
    post["links"][-1]["title"] = title
    await msg.reply("Ссылка сформирована", reply_markup=link_kb)


async def send_post(msg: types.Message, state: FSMContext):
    await state.finish()
    await view_post(post, chat_id=msg.from_user.id)
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

    dp.register_message_handler(pin_links, lambda msg: msg["from"]["id"] in ADMINS, commands=["test"],
                                state="*")
