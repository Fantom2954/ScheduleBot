from aiogram.types import (ReplyKeyboardMarkup,KeyboardButton,
                            InlineKeyboardMarkup,InlineKeyboardButton)
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message,CallbackQuery
from aiogram import F,Router

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Профиль"), KeyboardButton(text="Студенты")],
    [KeyboardButton(text="Расписание"), KeyboardButton(text="Задания")]
],
                resize_keyboard=True,
                input_field_placeholder='Выберите кнопку')

admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Профиль"), KeyboardButton(text="Студенты")],
    [KeyboardButton(text="Расписание"), KeyboardButton(text="Задания")]

],
               resize_keyboard=True,
               input_field_placeholder='Выберите кнопку')

setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сменить группу", callback_data="группы")]
])

groupprofill = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Группа 1101-H11",callback_data='группа1')],
    [InlineKeyboardButton(text="Группа 1101-н9",callback_data='группа2')],
    [InlineKeyboardButton(text="Группа  1102-н9",callback_data='группа3')]
    ])

расписание = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Группа 1101-H11",callback_data='группа4')],
    [InlineKeyboardButton(text="Группа 1101-н9",callback_data='группа5')],
    [InlineKeyboardButton(text="Группа  1102-н9",callback_data='группа6')]
    ])

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
           [ InlineKeyboardButton(text="Список учеников", callback_data="list_students"), InlineKeyboardButton(text="Рассылка", callback_data="enter_message")],
            [InlineKeyboardButton(text="Список заявок", callback_data="list_applications")],
                    
])

close_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Закрыть", callback_data="close_message")]])

accept_decline = InlineKeyboardMarkup(inline_keyboard=[

    [
        InlineKeyboardButton(text="Принять", callback_data=f"accept"),
        InlineKeyboardButton(text="Отклонить", callback_data="decline")
    ]
])
