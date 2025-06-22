import logging
import asyncio
import os
import re
import time
from datetime import datetime, timedelta

from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.fsm import state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from app.generators import *
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.generators import *
from app.handlers import show_waiting_animation
from app.states import Form, Sisyphus, Todo
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)

change_time = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Подкорректировать', callback_data='change_time'),
    ],
    [
        InlineKeyboardButton(text='Меню', callback_data='menu'),
    ]
])

menu_add = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить в список задач', callback_data='add_decomposer_task'),
    ],
    [
        InlineKeyboardButton(text='Меню', callback_data='menu'),
    ]
])

@router.callback_query(lambda c: c.data in ['todo_decomposer', 'todo_scheduler'])
async def new_task(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'todo_decomposer':
        await callback_query.message.answer(
            "<b>Декомпозитор: разбиваем задачу на шаги 🧩</b>\n\n"
            "Опишите вашу задачу или цель, которую нужно декомпозировать. Например:\n\n"
            "📌 <i>«Написать дипломную работу»</i>\n\n"
            "После этого ассистент предложит список шагов. Пример результата:\n"
            "1️⃣ Исследовать тему и собрать материалы\n"
            "2️⃣ Написать введение\n"
            "3️⃣ Составить основную часть\n"
            "4️⃣ Оформить и проверить работу\n\n"
            "Введите вашу задачу:",
            parse_mode="HTML"
        )
        await state.update_data(mode="decomposer")  # Сохраняем режим в state

    elif callback_query.data == 'todo_scheduler':
        await callback_query.message.answer(
            "<b>Планировщик: распределяем задачи по времени ⏰</b>\n\n"
            "Напишите список задач, которые хотите запланировать, и укажите время для каждой задачи. Например:\n\n"
            "📝 <i>«Изучить главы 1-3, написать конспект, повторить ключевые темы»</i>\n\n"
            "Пример:\n\n"
            "1️⃣ Изучить главы 1-3 – <i>14:00</i>\n"
            "2️⃣ Написать конспект – <i>16:00</i>\n"
            "3️⃣ Повторить ключевые темы – <i>18:00</i>\n\n"
            "Напишите ваш список задач и время для каждой из них.",
            parse_mode="HTML"
        )
        await state.update_data(mode="scheduler")  # Сохраняем режим в state
    print(111)
    await state.set_state(Todo.task)

@router.message(Todo.task)
async def get_task(message: Message, state: FSMContext):
    print(222)
    data = await state.get_data()
    mode = data.get("mode")  # Получаем режим (decomposer или scheduler)
    task = message.text
    print(333)
    if mode == "decomposer":
        # Промпт для декомпозирования
        prompt = (
            f"Разбей задачу «{task}» на конкретные, четкие шаги, "
            "которые помогут достичь цели."
        )

    elif mode == "scheduler":
        # Промпт для планирования
        prompt = (
            f"Помоги распределить задачи по времени. Мой список задач: {task}. "
            "Укажи, как можно логично распределить их по временным блокам. "
            "Пример ответа:\n\n"
            "<u>Распределение задач по времени:</u>\n\n"
            "1. <b>[Название задачи 1]</b> — 08:00-10:00 - <i>кратчайший совет (несколько слов)</i>\n"
        )
    a = await message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')

    request_task = asyncio.create_task(
        generator(
            user_id=message.from_user.id,
            content=prompt
        )
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id
    if mode == "scheduler":

        await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=change_time)
    else:
        await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=menu_add)

    await bot.delete_message(chat_id=message.chat.id, message_id=id[0])
    await state.clear()

@router.callback_query(lambda c: c.data in ['change_time'])
async def new_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "<b>⏰ Время для задач можно откорректировать!</b>\n\n"
        "Если вы хотите изменить время для каких-либо задач, укажите новые временные интервалы.\n"
        "Пример: <i>Задача 1 – 14:00</i>\n\n"
        "✏️ Просто напишите, какие изменения нужно внести, и мы их учтем!",
        parse_mode="HTML"
    )
    await state.set_state(Todo.time)

@router.message(Todo.time)
async def get_task(message: Message, state: FSMContext):
    task = message.text
    prompt = (f'откорректируй: {task}')
    a = await message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')

    request_task = asyncio.create_task(generator(user_id=message.from_user.id, content=prompt))

    await show_waiting_animation(a, request_task)

    response = await request_task

    await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=change_time)
    await bot.delete_message(chat_id=message.chat.id, message_id=a.message_id)

