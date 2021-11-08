from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button1 = KeyboardButton("Оставить заявку на звонок ⏳", request_contact=True)
button2 = KeyboardButton("Позвонить сейчас ☎️")
button3 = KeyboardButton("Выйти ❌")
button4 = KeyboardButton("Помощь ⚠️")

bot_kb = ReplyKeyboardMarkup(resize_keyboard=True)
bot_kb.add(button1).add(button2).row(button3, button4)

start_button = KeyboardButton("Войти снова ✋")
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(start_button)