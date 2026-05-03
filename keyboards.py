from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton

main_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="кнопка 1",callback_data="button_1"),InlineKeyboardButton(text="кнопка 2",callback_data="button_2")],
    [InlineKeyboardButton(text="кнопка 3",callback_data="button_3"),InlineKeyboardButton(text="кнопка 4",callback_data="button_4")]
])

main_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="кнопка 1"),KeyboardButton(text="кнопка 2")],
    [KeyboardButton(text="кнопка 3")]
])