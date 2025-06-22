import ast
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
from aiogram.filters import CommandStart, Command
from app.generators import *
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.generators import *
from app.handlers import show_waiting_animation
from app.states import Form, Sisyphus, Todo
from app.todo import show_tasks
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)


@router.callback_query(lambda c: c.data in ['add_decomposer_task'])
# @router.message(Command('dec'))
async def decomposer_todo(callback_query: CallbackQuery, state: FSMContext):
    # async def dec(message: Message):
    tasks = db.get_tasks(callback_query.from_user.id)
    a = await callback_query.message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')

    request_task = asyncio.create_task(
        generator(
            user_id=callback_query.from_user.id,
            content='''отправь декомпозированнное сообщение в формате списков
            отправь только списки и ничего более, текстом без разметки
            ['дело 1', описание, 18:30], ['дело 2', описание, 19:20]
        ''')
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id
    new = response
    fixed_new = f"[{new}]"
    new = ast.literal_eval(fixed_new)
    for i in new:
        tasks.append(i)
    db.update_tasks(callback_query.from_user.id, tasks)
    db.get_tasks(callback_query.from_user.id)
    await show_tasks(callback_query)

@router.message(Command('cleardb'))
async def clear_db(message: Message):
    db.update_tasks(message.from_user.id, tasks=[])
    await show_tasks(message)


@router.message(Command('c'))
async def clear_db(message: Message):
    a = "['Прыгать три раза', 'Найди безопасное место и подпрыгни три раза подряд', '18:30'], ['Один два', 'Сделай паузу и произнеси для концентрации', '18:35']"

    # Добавляем квадратные скобки, чтобы строка стала корректным списком
    fixed_a = f"[{a}]"
    a = ast.literal_eval(fixed_a)
    print(a)
    print(type(a))
