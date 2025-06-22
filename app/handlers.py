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
from app.states import Form
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)

logger = logging.getLogger(__name__)


async def show_menu(user_id):
    await bot.send_message(
        text='📋 <b>Вы попали в меню!</b> 📋\n\n'
             '⬇️ Ниже представлены все доступные функции ⬇️',
        reply_markup=kb.menu,
        chat_id=user_id,
        parse_mode='HTML'
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    print(db.get_info_up(message.from_user.id))
    user_id = message.from_user.id
    username = message.from_user.username
    command_args = message.text.split(' ')
    users = db.get_all_user_ids()

    logger.info(f"Пользователь ID: {user_id}, Username: {username} инициировал команду: '{message.text}'")

    # Проверка, если пользователь не в базе
    if user_id not in users:
        logger.info(f"Пользователь ID: {user_id} не найден в базе. Добавляем пользователя.")

        db.add_user(user_id=user_id,
                    username=username.lower(),
                    first_name=message.from_user.first_name)
        db.add_todo(user_id=user_id)
        logger.info(f"Пользователь ID: {user_id} добавлен в базу данных.")

        # Если есть реферальный код
        if len(command_args) > 1:
            ref_code = command_args[1]
            inviter_id = int(ref_code)
            logger.info(
                f"Пользователь ID: {user_id} пришел по реферальному коду: {ref_code}, ID пригласившего: {inviter_id}")

            a = str(db.get_ids())
            if (str(inviter_id) in a) and (str(user_id) != str(inviter_id)) and str(user_id) not in a:
                logger.info(f"Пользователь ID: {user_id} успешно пригласил {inviter_id}.")
                await message.answer(
                    f"🌀 Вы присоединились к <b>Сизифу</b> по реферальной ссылке от пользователя с ID: <b>{inviter_id}</b>! "
                    "Добро пожаловать в пространство развития и самодисциплины! ⚡",
                    parse_mode='HTML')

    if not db.get_thread(user_id):
        logger.info(f"Создаем тред для пользователя ID: {user_id}")
        thread = await client.beta.threads.create()
        thread_id = thread.id
        db.update_thread(user_id, thread_id)
        logger.info(f"Тред создан для пользователя ID: {user_id}, ID треда: {thread_id}")

    # Подписка на сервис
    if not db.get_subscription(user_id):
        logger.info(f"Пользователь ID: {user_id} не имеет подписки. Вставляем статус.")
        db.insert_status(user_id)

    if not db.get_motivation(user_id) or not db.get_dream(user_id):
        await message.answer(
            text='<b>Что тебя мотивирует?</b> 🤔 Напиши 2-3 вещи, которые вдохновляют тебя на достижения! 💭✨',
            parse_mode="HTML")
        await state.set_state(Form.motivation)


    else:
        logger.info(f"Отправляем приветственное сообщение пользователю ID: {user_id}")
        await message.answer(
            "<b>🚀 Добро пожаловать в Сизиф!</b>\n\n"
            "🔹 <b>Сизиф</b> — это путь преодоления, роста и поиска внутреннего стержня. "
            "Мы не даём лёгких решений, но предлагаем инструменты для формирования дисциплины и силы духа. 🏔\n\n"
            "🔥 Здесь вы узнаете, как работать с мотивацией, преодолевать прокрастинацию и идти к своим целям, "
            "несмотря на сложности. Вы готовы сделать первый шаг? Тогда начинаем! 💪",
            parse_mode='HTML'
        )

        logger.info(f"Отправляем меню пользователю ID: {user_id}")
        await bot.send_message(
            text='📌 <b>Главное меню</b>\n\n'
                 '🔻 Здесь вы найдете ключевые инструменты и задания для личностного роста. 🔻',
            reply_markup=kb.menu,
            chat_id=user_id,
            parse_mode='HTML'
        )
        await state.clear()


@router.callback_query(lambda c: c.data in ['menu'])
async def menu(callback_query: CallbackQuery, state: FSMContext):
    await show_menu(callback_query.from_user.id)


@router.message(Command('reset'))
async def cmd_start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду сброса.")
    thread = await client.beta.threads.create()
    thread_id = thread.id
    db.update_thread(message.from_user.id, thread_id)
    logger.info(f"Создан поток с ID {thread_id} для пользователя {message.from_user.id}.")


async def show_waiting_animation(message, request_task, delay=0.5):
    logger.info(f"Запуск анимации ожидания для сообщения {message.message_id}.")
    dots_animation = [
        "⏳ Пожалуйста, подождите.",
        "⏳ Пожалуйста, подождите..",
        "⏳ Пожалуйста, подождите...",
        "⌛ Пожалуйста, подождите...",
        "⌛ Пожалуйста, подождите..",
        "⌛ Пожалуйста, подождите."
    ]

    try:
        while not request_task.done():
            for dots in dots_animation:
                if request_task.done():
                    break
                await asyncio.sleep(delay)
                await message.edit_text(dots)
                logger.debug(f"Обновлено сообщение ожидания: {dots}")
    except asyncio.CancelledError:
        logger.warning("Анимация ожидания была отменена.")


@router.message(Command('test'))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду тест.")
    await message.answer('введите запрос')
    await state.set_state(Form.test)
    logger.info(f"Состояние пользователя {message.from_user.id} изменено на 'Form.test'.")


@router.message(Form.test)
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввел текст: {message.text}")
    text = message.text
    response = await generate_test(question=text, thread_id=db.get_thread(message.from_user.id))
    await message.answer(response)
    logger.info(f"Сгенерирован ответ для пользователя {message.from_user.id}: {response}")


@router.message(Command('today'))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду 'сегодня'.")
    start = db.get_sisyphus_date(message.from_user.id)
    today = datetime.now().strftime("%d-%m-%Y")

    start_date = datetime.strptime(start, '%d-%m-%Y')
    today_date = datetime.strptime(today, '%d-%m-%Y') + timedelta(days=1)

    day = (today_date - start_date).days
    a = await message.answer("⏳ Пожалуйста, подождите, идет обработка данных...", parse_mode='HTML')

    response = await generator(user_id=message.from_user.id, content=f'пришли план на день {day}')

    id[0] = a.message_id
    await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=kb.menu_button)
    await bot.delete_message(chat_id=message.chat.id, message_id=id[0])
    logger.info(f"Ответ на команду 'сегодня' отправлен пользователю {message.from_user.id}: {response}")


@router.message(Command('raz'))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду 'raz'.")
    response = await generator_nothread(
        content=f'Проанализируй мои ответы и четко сформулируй - что является моей истинной мечтой.'
                f'ответ должен быть максимально кратким'
                f'Чего ты хочешь? Хочу много денег\n'
                f'Почему это важно? Чтобы чувствовать себя в безопасности и быть независимым\n'
                f'Как это влияет на твою жизнь? Тогда я смогу сам выбирать, чем заниматься\n'
                f'Как это связано с твоими долгосрочными целями? Я хочу создать своё дело, которое будет помогать людям\n'
                f'Почему это так важно для тебя лично? Потому что я хочу чувствовать, что моя жизнь наполнена смыслом ✨\n\n',
        user_id=message.from_user.id)
    logger.info(f"Ответ для пользователя {message.from_user.id} по команде 'raz': {response}")


@router.message(Command('thread'))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вызвал команду 'thread'.")
    response = await get_thread_content(db.get_thread(message.from_user.id))

    for mes in response:
        await message.answer(f"{mes['role'].capitalize()}: {mes['text']}")
        logger.info(
            f"Отправлено сообщение для пользователя {message.from_user.id}: {mes['role'].capitalize()}: {mes['text']}")


@router.message(Command('t'))
async def cmd_start(message: Message, state: FSMContext):
    button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='t', callback_data='get_task_sis'), ],
    ])
    await message.answer(text='t', reply_markup=button)
    a = await message.answer("⏳ Пожалуйста, подождите, формируем вашу истинную мечту", parse_mode='HTML')

    request_task = asyncio.create_task(
        generator(
            user_id=message.from_user.id,
            content=f'Проанализируй мои ответы и четко сформулируй - что является моей истинной мечтой.'
                    f'ответ должен быть максимально кратким'
                    f'Чего ты хочешь? Хочу много денег\n'
                    f'Почему это важно? Чтобы чувствовать себя в безопасности и быть независимым\n'
                    f'Как это влияет на твою жизнь? Тогда я смогу сам выбирать, чем заниматься\n'
                    f'Как это связано с твоими долгосрочными целями? Я хочу создать своё дело, которое будет помогать людям\n'
                    f'Почему это так важно для тебя лично? Потому что я хочу чувствовать, что моя жизнь наполнена смыслом ✨\n\n'

        )
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id

    await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=kb.menu_button)
    await bot.delete_message(chat_id=message.from_user.id, message_id=id[0])
