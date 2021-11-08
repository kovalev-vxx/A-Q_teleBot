from db.db import Users, Bans, engine, get_session, upload_to_users, remove_from_db, upload_to_bans
from create_bot import bot, ADMINS
from keyboards.admin_kb import *
from aiogram import types, Dispatcher
from utils.replies import *


async def start_admin(msg: types.Message):
    session = get_session(engine)
    upload_to_users(user=msg.from_user, session=session)
    await msg.reply("Привет админ", reply_markup=main_kb, reply=False)


class UnknownUser(Exception):
    pass


ban_btn = InlineKeyboardButton('Заблокировать', callback_data='ban')
unban_btn = InlineKeyboardButton('Разблокировать', callback_data='unban')
ban_kb = InlineKeyboardMarkup().add(ban_btn)
unban_kb = InlineKeyboardMarkup().add(unban_btn)


async def ban(msg: types.Message):
    ban_id = msg.get_args()
    print(ban_id)
    try:
        session = get_session(engine)
        user = session.query(Users).filter(Users.user_id == ban_id).all()
        if user:  # user is registered?
            upload_to_bans(session=session, user=user[0])
            await msg.reply(f"Пользователь {ban_id} заблокирован\n\n#ban", reply_markup=unban_kb, reply=False)
        else:
            raise UnknownUser
    except UnknownUser:
        await msg.reply("Такого пользователя не существет", reply_markup=main_kb, reply=False)


async def ban_unban_msg(callback_query: types.CallbackQuery):
    msg = callback_query.message
    action = callback_query.data
    session = get_session(engine)
    user_id = msg.text.split()[1]
    if action == "unban":
        edited_text = msg.text.replace("заблокирован", "разблокирован")
        remove_from_db(session=session, db=Bans, user_id=user_id)
        await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=edited_text,
                                    reply_markup=ban_kb)
    elif action == "ban":
        edited_text = msg.text.replace("разблокирован", "заблокирован")
        user = session.query(Users).filter(Users.user_id == user_id).all()
        upload_to_bans(session=session, user=user[0])
        await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=edited_text,
                                    reply_markup=unban_kb)


async def get_users_list(msg: types.Message):
    session = get_session(engine)
    users = session.query(Users).all()
    if users:
        answer = users_list(users)
        await msg.reply(answer, reply=False)
    else:
        await msg.reply("Список пуст", reply=False)


async def get_ban_list(msg: types.Message):
    session = get_session(engine)
    users = session.query(Bans).all()
    if users:
        answer = users_list(users)
        await msg.reply(answer, reply=False)
    else:
        await msg.reply("Список пуст", reply=False)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_admin, lambda msg: msg["from"]["id"] in ADMINS, commands=["start"])
    dp.register_message_handler(ban, lambda msg: msg["from"]["id"] in ADMINS, commands=["ban"])
    dp.register_callback_query_handler(ban_unban_msg, lambda c: c.data == "unban" or c.data == "ban")
    dp.register_message_handler(get_users_list, lambda msg: msg["from"]["id"] in ADMINS and msg.text == button1.text)
    dp.register_message_handler(get_ban_list, lambda msg: msg["from"]["id"] in ADMINS and msg.text == button2.text)
