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
from app.todo import show_tasks
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)

# from dateutil import parser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import logging



logging.basicConfig(level=logging.INFO)
async def show_task_details(entity, state: FSMContext):
    tasks = db.get_tasks(entity.from_user.id)
    data = await state.get_data()

    if isinstance(entity, CallbackQuery):
        task_index = int(entity.data.split('_')[1])

    elif isinstance(entity, Message):
        task_index = int(data.get('task_index', 0))

    await state.update_data(task_index=task_index)

    task_about = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📝 Добавить описание', callback_data=f'adddescription_{task_index}')],
        [InlineKeyboardButton(text='⏰ Добавить напоминание', callback_data=f'addreminder_{task_index}')],
        [InlineKeyboardButton(text='✅ Выполнена (удалить) ❌', callback_data=f'delete_{task_index}')],
    ])

    text = f'<b>💼 Задача:</b> {tasks[task_index][0]}\n\n'

    if tasks[task_index][1]:
        text += f'<b>📝Описание:</b> {tasks[task_index][1]}\n\n'
    if tasks[task_index][2]:
        text += f'<b>⏰Напоминание:</b> {tasks[task_index][2]}\n\n'

    if isinstance(entity, Message):
        await entity.answer(
            text=text,
            reply_markup=task_about,
            parse_mode='HTML'
        )
    elif isinstance(entity, CallbackQuery):
        await entity.message.answer(
            text=text,
            reply_markup=task_about,
            parse_mode='HTML'
        )


@router.callback_query(lambda c: c.data.startswith('about_'))
async def about_task(callback_query: CallbackQuery, state: FSMContext):
    await show_task_details(callback_query, state)


@router.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_task(callback_query: CallbackQuery):
    tasks = db.get_tasks(callback_query.from_user.id)
    task_index = int(callback_query.data.split('_')[1])
    tasks.pop(task_index)
    db.update_tasks(user_id=callback_query.from_user.id, tasks=tasks)
    await callback_query.answer(
        f'✅ Задача успешно удалена.'
    )
    await show_tasks(callback_query)


@router.callback_query(lambda c: c.data.startswith('adddescription_'))
async def add_description_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text='<b>📝 Введите описание задачи:</b>\n\n'
             '<i>Пожалуйста, напишите подробности о вашей задаче. Это поможет вам не забыть важные моменты! 💡</i>',
        parse_mode='HTML'
    )
    await state.set_state(Todo.description)



@router.message(Todo.description)
async def save_new_task(message: Message, state: FSMContext):
    description = message.text
    tasks = db.get_tasks(message.from_user.id)
    data = await state.get_data()
    task_index = int(data['task_index'])
    tasks[task_index][1] = description

    db.update_tasks(user_id=message.from_user.id, tasks=tasks)
    await state.clear()
    await show_task_details(message, state)


@router.callback_query(lambda c: c.data.startswith('addreminder_'))
async def add_description_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text='<b>⏰ Введите время для напоминания:</b>\n\n'
             '<i>Пожалуйста, укажите время в следующем формате:</i>\n'
             '<b>Сегодня в 15:30</b> или <b>Через 5 минуь</b>\n',
        parse_mode='HTML'
    )
    await state.set_state(Todo.reminder)


@router.message(Todo.reminder)
async def save_new_task(message: Message, state: FSMContext):
    time = message.text
    tasks = db.get_tasks(message.from_user.id)
    data = await state.get_data()
    task_index = int(data['task_index'])
    # Обработка выражения "послезавтра"
    if 'послезавтра' in time.lower():
        today = datetime.today()
        time = time.lower().replace('послезавтра', 'через два дня')

    if 'через минуту' in time.lower():
        time = (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
    elif 'через полчаса' in time.lower():
        time = (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M')
    elif 'через' in time.lower() and 'минут' in time.lower():
        try:
            minutes = int([word for word in time.split() if word.isdigit()][0])
            time = (datetime.now() + timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M')
        except (ValueError, IndexError):
            pass  # Если не удается извлечь число, оставляем оригинальный текст

    try:
        # Попробуем распарсить время с помощью dateutil.parser
        # parsed_time = parser.parse(time, fuzzy=True)

        # Если время распарсилось, применяем к нему формат
        if 'через два дня' in time.lower():
            parsed_time = today + timedelta(days=2)

        # Преобразуем время в нужный формат
        formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M')
        print(formatted_time)
        # Добавление задачи в планировщик
        scheduler = AsyncIOScheduler()

        # Добавляем задачу напоминания в планировщик с заданным временем
        scheduler.add_job(
            send_reminder,
            trigger=DateTrigger(run_date=parsed_time),
            args=[message.from_user.id, parsed_time, bot, tasks, task_index],  # передаем user_id, время и объект bot
            id=f"reminder_{message.from_user.id}_{parsed_time}",
            replace_existing=True
        )

        # Стартуем планировщик
        scheduler.start()
        tasks[task_index][2] = formatted_time

        db.update_tasks(user_id=message.from_user.id, tasks=tasks)
        await message.answer(
            text=f"<b>⏰ Напоминание на {formatted_time} установлено!</b>\n<i>Не забудьте о задаче! 🎯</i>",
            parse_mode='HTML'
        )
        await show_tasks(message)

    except (ValueError, OverflowError) as e:
        # Если не удалось распарсить время, отправляем сообщение об ошибке
        await message.answer(
            "❌ Не удалось распознать время. Пожалуйста, используйте один из предложенных форматов."
        )


async def send_reminder(user_id, reminder_time, bot, tasks, task_index):
    tasks=tasks[task_index]
    print(tasks)
    await bot.send_message(
        chat_id=user_id,
        text=f"<b>💼 Задача:</b> {tasks[0]}\n\n"
             f"<b>📝 Описание:</b> {tasks[1]}\n\n"
             f"<b>⏰ Напоминание:</b> {tasks[2]}\n",
        parse_mode='HTML'
    )

