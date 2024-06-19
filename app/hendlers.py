from aiogram import F,Router
import sqlite3 as sq
import asyncio
from aiogram.utils.markdown import link

import time

from aiogram.types import Message,CallbackQuery
from aiogram.filters import CommandStart,Command
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from confing import TOKEN
from app import database as db
from aiogram.utils.markdown import hbold
import app.keyboards as kb 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Tuple
from collections import defaultdict
import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
Base = declarative_base()

router = Router()
load_dotenv()
bot = Bot(token=TOKEN)
dp = Dispatcher()

#router.message(process_group, state="*") 
group_names = {
    "1101-H11": "1101-H11",
    "1101-н9": "1101-н9",
    "1102-н9": "1102-н9",
}
# /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await db.cmdstart(message.from_user.id, message.from_user.username)

    if str(message.from_user.id) in db.get_admin_ids():
        return await message.answer("Добро пожаловать в бота <b>Hexlet.</b> \n"
                                    "Вы - Admin",
                                    reply_markup=kb.main,
                                    parse_mode="HTML")

    user_group = await db.get_user_group(message.from_user.id)
    if user_group:
        group_name = group_names.get(user_group, "Неизвестная группа")
        await message.answer(f"Добро пожаловать в бота <b>Hexlet.</b> \n"
                             f"Вы уже в группе {group_name}.",
                             reply_markup=kb.main,
                             parse_mode="HTML") 
        return

    await message.answer("Добро пожаловать в бота <b>Hexlet.</b> \n"
                         "Напишите вашу группу (1101-H11, 1101-н9, 1102-н9)",
                         reply_markup=kb.main,
                         parse_mode="HTML") 

#admin
@router.message(F.text == "/admin")
async def welcome_user(message: Message):
    admin_ids = db.get_admin_ids()
    user_id = str(message.from_user.id) 

    if user_id in admin_ids:
        await message.reply('<b>👑 Добро пожаловать, в Админ-панель</b>', reply_markup=kb.admin_panel,parse_mode="HTML")
    else:
        await message.reply('<b>🚫 У вас нет доступа к админ-панели</b>', parse_mode="HTML") 

#id
@router.message(F.text == '/id')
async def id(message: Message):
    await message.answer(f'Ваш ID: <b>{message.from_user.id}</b>',parse_mode='HTML')

#profil
@router.message(F.text == "Профиль")
async def welcome_user(message: Message):
    user_id = message.from_user.id
    group_name = await db.get_user_group(user_id)  

    if str(user_id) in db.get_admin_ids():
        await message.answer("<b>Вы - администратор. У вас нет группы.</b>", reply_markup=kb.close_markup, parse_mode="HTML")
    elif group_name: 
        await message.answer(f'''<blockquote><b>Добро пожаловать, @{message.from_user.username}</b></blockquote>
        \n<blockquote><b>Ваша группа: {group_name}</b></blockquote>
        <blockquote><b>Новых заданий: 0</b></blockquote>
        \n<b>Сегодня занятия:\n начинаются с 9:00 до 16:10/нету(comming soon..) </b>
        \n<b>Завтра занятия:\n начинаются с 9:00 до 15:20/нету(comming soon..)</b>''', reply_markup=kb.setting, parse_mode="HTML")
    else:
        await message.answer("Вы не состоите ни в одной группе.") 

@router.callback_query(F.data == "close_message")
async def close_message_handler(callback: CallbackQuery):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer()
#в разработке 

#Смена групп
@router.callback_query(F.data.startswith('группы'))
async def handle_group_selection(callback_query: types.CallbackQuery):
        await callback_query.message.answer("Выбери на какую группу хотите сменить",reply_markup=kb.groupprofill)

@router.callback_query(F.data == 'группа1')
async def handle_group_1101_H11(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    selected_group = '1101-H11'

    try:
        conn = sq.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            current_group = result[0]
            # Отправка запроса администраторам на утверждение
            admin_ids = get_admin_ids()
            for admin_id in admin_ids:
                admin_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_group_change_{user_id}_{selected_group}"),
                     InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_group_change_{user_id}")]
                ])
                await bot.send_message(
                    admin_id,
                    f"Пользователь @{username} (ID: {user_id}) хочет изменить свою группу с {current_group} на {selected_group}.",
                    reply_markup=admin_markup
                )

            await callback_query.answer("Запрос отправлен администратору. Ожидайте подтверждения.")
            await state.clear()
        else:
            await callback_query.answer("Вы не состоите ни в одной группе.")

    except Exception as e:
        await callback_query.message.answer(f"Ошибка при обработке запроса: {e}")

@router.callback_query(F.data == 'группа2')
async def handle_group_1101_n9(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    selected_group = '1101-н9'

    try:
        conn = sq.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            current_group = result[0]
            # Send request to admins for approval
            admin_ids = get_admin_ids()
            for admin_id in admin_ids:
                admin_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_group_change_{user_id}_{selected_group}"),
                     InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_group_change_{user_id}")]
                ])
                await bot.send_message(
                    admin_id,
                    f"Пользователь @{username} (ID: {user_id}) хочет изменить свою группу с {current_group} на {selected_group}.",
                    reply_markup=admin_markup
                )

            await callback_query.answer("Запрос отправлен администратору. Ожидайте подтверждения.")
            await state.clear()
        else:
            await callback_query.answer("Вы не состоите ни в одной группе.")

    except Exception as e:
        await callback_query.message.answer(f"Ошибка при обработке запроса: {e}")

@router.callback_query(F.data == 'группа3')
async def handle_group_1102_n9(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    selected_group = '1102-н9'

    try:
        conn = sq.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            current_group = result[0]
            # Send request to admins for approval
            admin_ids = get_admin_ids()
            for admin_id in admin_ids:
                admin_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_group_change_{user_id}_{selected_group}"),
                     InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_group_change_{user_id}")],
                ])
                await bot.send_message(
                    admin_id,
                    f"Пользователь @{username} (ID: {user_id}) хочет изменить свою группу с {current_group} на {selected_group}.",
                    reply_markup=admin_markup
                )

            await callback_query.answer("Запрос отправлен администратору. Ожидайте подтверждения.")
            await state.clear()
        else:
            await callback_query.answer("Вы не состоите ни в одной группе.")

    except Exception as e:
        await callback_query.message.answer(f"Ошибка при обработке запроса: {e}")

#кнопки для принятите сменны группы
@router.callback_query(F.data.startswith('accept_group_change_'))
async def accept_group_change(callback_query: types.CallbackQuery, bot: Bot):
    data = callback_query.data.split('_')
    user_id = int(data[3])
    selected_group = data[4]

    try:
        conn = sq.connect('database.db')
        cursor = conn.cursor()

        # Получить текущую группу пользователя перед обновлением
        cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        current_group = result[0] if result is not None else "None"

        # Обновить группу пользователя
        cursor.execute("UPDATE users SET group_name = ? WHERE user_id = ?", (selected_group, user_id))
        conn.commit()
        conn.close()

        # Отправить подтверждающие сообщение администратору
        await bot.send_message(user_id, f"Администратор подтвердил изменение вашей группы с {current_group} на {selected_group}.")
        await callback_query.answer("Вы подтвердили изменение группы.")

    except Exception as e:
        await callback_query.answer(f"Ошибка при изменении группы: {e}")

# Отклонение группы
@router.callback_query(F.data.startswith('decline_group_change_'))
async def decline_group_change(callback_query: types.CallbackQuery, bot: Bot):
    user_id = int(callback_query.data.split('_')[3])
    
    await bot.send_message(user_id, "Администратор отклонил ваш запрос на изменение группы.")
    await callback_query.answer("Вы отклонили изменение группы.")
 
#в разработке 
@router.message(F.text == "Расписание")
async def welcome_user(message):
    await message.answer('Выберите группу:',reply_markup=kb.расписание)

#расписание
@router.callback_query(F.data=='группа4')
async def расписание(callback_query: types.CallbackQuery):
    await callback_query.message.answer(f'''<b>Понедельник-17.06.2024
#Занятия
09:00   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л)</a>
10:35   Петрушкин К.
        Аудитория (НСК)
10:45   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л)</a>
12:20   Петрушкин К.
        Аудитория (НСК)
12:50   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Основы алгоритмизации и программирования_Петрушкин (Нск)(ПР)</a>
14:25   Петрушкин К.
        Аудитория (НСК)</b>
                           
<b>Вторник-18.06.2024
#	Занятия
09:00   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л)</a>
10:35   Петрушкин К.
        Аудитория (НСК)
10:45   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л) </a>
12:20   Петрушкин К.
        Аудитория (НСК)</b>
                                        
<b>Среда(сегодня)-19.06.2024
#	Занятия
09:00   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л) </a>
10:35   Петрушкин К.
        Аудитория (НСК)
10:45   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л) </a>
12:20   Петрушкин К.
        Аудитория (НСК)
12:50 <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Разработка програм.модулей_Петрушкин (Нск)(Л) </a>
14:25   Петрушкин К.
        Аудитория (НСК)</b>
                                    
<b>Четверг-20.06.2024
#	Занятия                                     
12:50   <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Теория вероятностей и математическая статистика_Фархетдинова(ПР)</a>
14:25   Фархетдинова(НСК)
        Онлайн_Фархетдинова
14:35<a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Ин. язык в проф. деятельности - Жернакова (онлайн)</a>
16:10   Жернакова(НСК)
        МСК НАЧАЛО 10:35</b>
                                        
<b>Пятница-21.06.2024
#	Занятия                                      
10:45 <a href='https://zoom.us/j/3824133784?pwd=bVdublNNT1ZkYXZvRjYrQlBxMkV2dz09'>Физкультура</a>
12:20   Кузнецов А. И.
        Кузнецов А. И.
        НСК_Б.Хмельницкого 2 (начало в 10.40)</b>
                                        
<b>Суббота-22.06.2024
# Занятия
Нет занятий</b>''',parse_mode="HTML")

# Список студентов
@router.callback_query(F.data == 'list_students')
async def handle_list_students(call: types.CallbackQuery):
    conn = sq.connect('database.db')
    cur = conn.cursor()
    query = "SELECT user_id, username, group_name FROM users WHERE status = 1"
    cur.execute(query)
    students = cur.fetchall()
    conn.close()

    if students:
        student_list = "\n".join([f"ID: {student[0]}, Username: @{student[1]} Группа: {student[2]}" for student in students])
        await call.message.answer(f"<b>Список учеников:</b>\n{student_list}",parse_mode="HTML")
    else:
        await call.message.answer("Список учеников пуст.")

#список заявок
conn = sq.connect('database.db')
cursor = conn.cursor()

class ApplicationState(StatesGroup):
    application_data = State()

#Рассылка
class BroadcastMessage(StatesGroup):
    WAITING_FOR_MESSAGE = State()

@router.callback_query(F.data == 'enter_message')
async def handle_enter_message(call: types.CallbackQuery, state: FSMContext):
    admin_ids = db.get_admin_ids()
    if str(call.from_user.id) in admin_ids:
        await state.set_state(BroadcastMessage.WAITING_FOR_MESSAGE)
        await call.message.answer("<b>Введите текст сообщения, которое нужно отправить всем пользователям:\n\n"
                                 "Отправьте \"отмена\", чтобы отменить рассылку.</b>",parse_mode="HTML")
    else:
        await call.message.answer("У вас нет прав для этой команды.")

@router.message(BroadcastMessage.WAITING_FOR_MESSAGE)
async def process_soon_message(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Рассылка отменена.")
        return

    try:
        with sq.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users")
            users = cur.fetchall()

            for user_id in users:
                try:
                    await bot.send_message(chat_id=user_id[0], text=message.text)
                except Exception as e:
                    print(f"Ошибка при отправке сообщения пользователю {user_id[0]}: {e}")
                    await message.answer(f"Ошибка при отправке сообщения пользователю {user_id[0]}.")

        await message.answer("Рассылка завершена.")
        await state.clear()

    except Exception as e:
        await message.answer(f"Произошла ошибка при работе с базой данных: {e}")
        await message.answer("Рассылка завершена. Сообщение отправлено (успешно/некоторым) пользователям.")

#принять в группу 
@router.callback_query(F.data == 'list_applications')
async def handle_list_applications(call: types.CallbackQuery, state: FSMContext):
    try:
        # Подключение к базе данных
        conn = sq.connect('database.db')
        cursor = conn.cursor()

        # Получение доступа
        cursor.execute("SELECT user_id, username, group_name FROM users")
        applications = cursor.fetchall()

        # Проверка и форматирование списка
        if applications:
            pending_applications = [
                app for app in applications if app[2] is None or app[2] == '' and str(app[0]) not in db.get_admin_ids()
            ]
            if pending_applications:
                pending_list = "\n".join(
                    [f"ID: <b>{app[0]}</b>, Username: @{app[1]}, Group Name: <b>{app[2] if app[2] else 'Указана в заявке'}</b>" for app in pending_applications]
                )
                await call.message.answer(f"Список ожидающих заявок:\n{pending_list}", parse_mode="HTML")
            else:
                await call.message.answer("Список ожидающих заявок пуст.")
            await state.set_state('group_name')
        else:
            await call.message.answer("Список заявок пуст.")
    except Exception as e:
        await call.message.answer(f"Ошибка при получении списка заявок: {e}")
    finally:
        if conn:
            conn.close()
            
@router.message(F.text)
async def process_group(message: Message, state: FSMContext):
    user_id = message.from_user.id
    group_name = message.text.strip()

    if str(user_id) in db.get_admin_ids():
        return

    existing_group = await db.get_user_group(user_id)
    if existing_group is not None:
        return  

    if group_name in group_names:
     
        for admin_id in db.get_admin_ids():
            admin_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}_{group_name}"), 
                 InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{user_id}")]
            ])
            await bot.send_message(
                admin_id,
                f"Пользователь @{message.from_user.username} (ID: {user_id}) хочет вступить в группу {group_name}.",
                reply_markup=admin_markup
            )
        await message.answer("Ваша заявка отправлена администратору.")
    else:
        await message.answer("Неверный номер группы. Пожалуйста, введите корректное название группы.")
#Принятие и отклонение в группу

@router.callback_query(F.data.startswith('accept_'))
async def accept_action(callback: CallbackQuery, bot: Bot):
    try:
        user_id = int(callback.data.split('_')[1])
        group_name = callback.data.split('_')[2] 

        if await db.save_user_group(user_id, group_name):
            await bot.send_message(user_id, f"Вы были приняты в группу {group_name}!")
            await callback.answer("Пользователь принят")  # Ответить на запрос обратного вызова
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await bot.send_message(user_id, "Произошла ошибка при добавлении в группу. Обратитесь к администратору.")
            await callback.answer("Ошибка добавления")  # Ответ с ошибкой
    except Exception as e:
        print(f"Error in accept_action: {e}")  # Запись ошибки
        await callback.answer("Произошла ошибка") 

@router.callback_query(F.data.startswith('decline_'))
async def decline_action(callback: CallbackQuery, bot: Bot):
    try:
        user_id = int(callback.data.split('_')[1])
        await bot.send_message(user_id, 'Ваша заявка отклонена.')
        await callback.answer("Заявка отклонена")
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"Error in decline_action: {e}") 
        await callback.answer("Произошла ошибка")
# Анти-спам система
MESSAGE_LIMIT = 10
TIME_FRAME = 5
INITIAL_BAN_DURATION = 10 

def get_admin_ids():
    conn = sq.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE status=2")
    admin_ids = [str(row[0]) for row in cur.fetchall()]
    conn.close()
    return admin_ids

user_data: Dict[int, Tuple[list, float, int]] = defaultdict(lambda: ([], 0, 0))

async def antispam_middleware(handler, event: Message, data):
    """Middleware function to check for spam, delete messages, 
       ban users with increasing ban durations, 
       and send ban messages with remaining time.
    """
    user_id = event.from_user.id
    current_time = time.time()

    admin_ids = get_admin_ids() 
    if str(user_id) in admin_ids:
        return await handler(event, data)  

    message_history, ban_time, ban_count = user_data[user_id]

    # Проверка на бан
    if current_time < ban_time:
        try:
            await event.delete()  

            remaining_time = int(ban_time - current_time)
            time_until_unban = str(datetime.timedelta(seconds=remaining_time))

            await event.answer(f"Вы заблокированы ещё на {time_until_unban}.")

        except Exception as e:
            print(f"Error handling ban: {e}") 
        return  

    message_history = [
        timestamp for timestamp in message_history
        if current_time - timestamp <= TIME_FRAME
    ]

    user_data[user_id] = (message_history, ban_time, ban_count)

    if len(message_history) >= MESSAGE_LIMIT:
        ban_count += 1
        ban_duration = INITIAL_BAN_DURATION * ban_count 

        # Бан пользователя
        user_data[user_id] = ([], current_time + ban_duration, ban_count)

        try:
            await event.delete()  
            await event.answer(
                f"Вы заблокированы на {ban_duration} секунд за повторный спам."
            )
        except Exception as e:
            print(f"Error handling ban: {e}")  
        return  

    message_history.append(current_time)
    return await handler(event, data)

router.message.middleware(antispam_middleware)