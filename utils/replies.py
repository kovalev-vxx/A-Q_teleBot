from aiogram.utils.markdown import text, bold, italic, code, pre
from typing import NamedTuple
from aiogram.types import Message


class Contact(NamedTuple):
    id: str
    name: str
    phone_number: str
    chat_id: int
    date: str


def user_info_parser(msg: Message) -> Contact:
    user_id = f"""@{msg["from"]["username"]}""" if msg["from"]["username"] != None else "\*Неизвестно\*"
    date = msg["date"]
    name = f"""{msg["contact"]["first_name"]} {msg["contact"]["last_name"]}"""
    phone_number = f"""+{msg["contact"]["phone_number"]}"""
    chat_id = msg["from"]["id"]
    return Contact(id=user_id,
                   name=name,
                   phone_number=phone_number,
                   date=date,
                   chat_id=chat_id)


def users_list(users):
    msg = ["№ | Имя | Chat_ID | Никнейм "]
    n = 0
    for user in users:
        if user.is_admin:
            continue
        name = f"{user.first_name} {user.last_name}" if user.last_name else f"{user.first_name}"
        id = f"{user.user_id}"
        n += 1
        username = f"@{user.username}" if user.username else None
        msg.append(
            f"{n}. {name} {id} {username}"
        )
    return "\n\n".join(msg)


# TODO ДОДЕЛАТЬ


def sendContactToAdmin(contact: Contact):
    msg = text(
        "Пришла новая заявка на звонок!\n",
        bold("Имя: "), f"""{contact.name}\n""",
        bold("Номер телефона: "), f"""{contact.phone_number}\n""",
        bold("ID в Telegram: "), f"""{contact.id}\n\n""",
        bold("Chat ID: "), f"""{contact.chat_id}\n\n""",
        code(f"""{contact.date}""")
    )
    return msg


def callMeAnswer():
    msg = text(
        "Вы можете позвонить по номеру:\n",
        "+79999999999\n",
        "Меня зовут ", bold("Григорий\n"),
        "Доступен с 9:00 до 18:00"
    )
    return msg


def thankYouMsg():
    msg = text(
        bold("Спасибо за обращение 😄 \n"),
        "Вам ответят в течение 24 часов"
    )
    return msg


def startAnswer(first_name, last_name):
    name = first_name
    if last_name:
        name += f" {last_name}"

    msg = text(
        bold("Здравсвуйте"), f"{name}!"
    )
    return msg
