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
from app.states import Form, Sisyphus, Todo
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)


async def show_tasks(entity):
    tasks = db.get_tasks(entity.from_user.id)
    print(tasks)
    task_buttons = [
        [InlineKeyboardButton(text=task[0], callback_data=f'about_{i}_{task[0]}')]  # Извлекаем строку из списка
        for i, task in enumerate(tasks)
    ]
    task_buttons.append([
        InlineKeyboardButton(text='📋 Меню', callback_data='menu'),
        InlineKeyboardButton(text='➕ Добавить задачу', callback_data='todo_new_task')
    ])
    task_buttons.append([
        InlineKeyboardButton(text='🗑 Очистить все', callback_data='clearall')
    ])

    task_menu = InlineKeyboardMarkup(inline_keyboard=task_buttons)

    if not tasks:
        await bot.send_message(
            chat_id=entity.from_user.id,
            text='<b>🚫 Список задач пуст.</b>',
            reply_markup=task_menu,
            parse_mode='HTML'
        )
        return

    tasks_text = "<b>📋 Ваши задачи:</b>\n\n" \
                 "Выберите задачу, чтобы добавить к ней описание или установить напоминание. 🖋️"

    if isinstance(entity, Message):
        await entity.answer(
            text=tasks_text,
            reply_markup=task_menu,
            parse_mode='HTML'
        )
    elif isinstance(entity, CallbackQuery):
        await entity.message.answer(
            text=tasks_text,
            reply_markup=task_menu,
            parse_mode='HTML'
        )


@router.callback_query(lambda c: c.data == 'todo')
async def view_tasks(callback_query: CallbackQuery):
    task_function_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ ToDo (простой список задач)', callback_data='todo_todo')],
        [InlineKeyboardButton(text='🧩 Декомпозитор (разбить план)', callback_data='todo_decomposer')],
        [InlineKeyboardButton(text='⏰ Планировщик (распределить задачи)', callback_data='todo_scheduler')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='menu')],

    ])
    await callback_query.message.answer(
        "<b>Выберите нужный инструмент для работы с задачами:</b>\n\n"
        "✅ <b>ToDo</b> – простой список задач. Подходит для ведения списка дел: "
        "добавляйте, отмечайте выполненные или удаляйте задачи.\n\n"
        "🧩 <b>Декомпозитор</b> – помогает разбить сложный план на отдельные шаги. "
        "Используйте, если задача слишком большая и требует деления на части.\n\n"
        "⏰ <b>Планировщик</b> – распределяет задачи по времени. "
        "Укажите, когда выполнить каждый шаг, чтобы успеть вовремя.\n\n"
        "Выберите подходящую функцию и начните планировать!",
        parse_mode="HTML",
        reply_markup=task_function_menu
    )


@router.callback_query(lambda c: c.data == 'todo_todo')
async def view_tasks(callback_query: CallbackQuery):
    await show_tasks(callback_query)


@router.callback_query(lambda c: c.data == 'todo_new_task')
async def create_new_task(callback_query: CallbackQuery, state: FSMContext):
    a = await callback_query.message.edit_text(
        text='<b>✍️ Введите текст задачи:</b>',
        parse_mode='HTML'
    )
    id[0] = a.message_id
    await state.set_state(Todo.awaiting_task)


@router.message(Todo.awaiting_task)
async def save_new_task(message: Message, state: FSMContext):
    task_text = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=id[0])
    tasks = db.get_tasks(message.from_user.id)
    tasks.append([task_text, None, None])

    db.update_tasks(user_id=message.from_user.id, tasks=tasks)
    await state.clear()
    await show_tasks(message)


@router.callback_query(lambda c: c.data == 'clearall')
async def clear(callback_query: CallbackQuery, state: FSMContext):
    db.update_tasks(callback_query.from_user.id, tasks=[])
    await show_tasks(callback_query)
