from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

button1 = KeyboardButton("Список пользователей")
button2 = KeyboardButton("Бан-лист")
button3 = KeyboardButton("Режим публикации")
button4 = KeyboardButton("Помощь ⚠️")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(button3).row(button2, button4, button1)
