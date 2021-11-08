from db.db import Users, Bans, engine, get_session, upload_to_users, remove_from_db
from aiogram import types, Dispatcher
from aiogram.types import ContentType, ParseMode
from utils.replies import *
from keyboards.client_kb import *
from create_bot import ADMINS, bot


def auth(func):
    async def wrapper(message):
        session = get_session(engine)
        users = session.query(Users).filter(Users.user_id == message["from"]["id"]).all()
        users = [i.user_id for i in users]
        if message["from"]["id"] not in users:
            return await message.reply("Вы не зарегистрированы! Для регистрации напишите /start", reply=False)
        return await func(message)

    return wrapper


def ban_check(func):
    async def wrapper(message):
        session = get_session(engine)
        users = session.query(Bans).filter(Bans.user_id == message["from"]["id"]).all()
        print(users)
        users = [i.user_id for i in users]
        print(users)
        if message["from"]["id"] in users:
            return await message.reply("Вы заблокированы", reply=False)
        return await func(message)

    return wrapper


async def start_command(msg: types.Message):
    session = get_session(engine)
    if upload_to_users(user=msg.from_user, session=session):
        answer = startAnswer(first_name=msg.from_user["first_name"], last_name=msg.from_user["last_name"])
        await msg.reply(answer, reply_markup=bot_kb, reply=False)
    else:
        await msg.reply("Вы уже зарегестрированы", reply_markup=bot_kb, reply=False)


@ban_check
@auth
async def get_contact(msg: types.Message):
    contact_info = user_info_parser(msg)
    answer_for_admin = sendContactToAdmin(contact_info)
    answer = thankYouMsg()
    await msg.reply(answer, reply=False, reply_markup=bot_kb, parse_mode=ParseMode.MARKDOWN)
    for user_id in ADMINS:
        await bot.send_message(user_id, answer_for_admin, parse_mode=ParseMode.MARKDOWN)


@ban_check
@auth
async def call_me(message: types.Message):
    answer = callMeAnswer()
    await message.reply(answer, reply_markup=bot_kb, reply=False, parse_mode=ParseMode.MARKDOWN)


@auth
async def remove_me(msg: types.Message):
    session = get_session(engine)
    remove_from_db(session=session, user_id=msg.from_user.id, db=Users)
    await msg.reply("До скорых встреч! Я забыл тебя", reply_markup=start_kb, reply=False)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_command, lambda msg: msg.text == "/start" or msg.text == start_button.text)
    dp.register_message_handler(get_contact, content_types=ContentType.CONTACT)
    dp.register_message_handler(call_me, lambda msg: msg.text == button2.text)
    dp.register_message_handler(remove_me, lambda msg: msg.text == button3.text)

