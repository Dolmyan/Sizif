from asyncio import Semaphore

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
from config import *
from database import BotDB
import app.keyboards as kb
from app.generators import *

db = BotDB('sizif_mode.db')


async def send_notifications(bot, content_template, time_of_day):
    """
    Отправляет уведомления всем пользователям.

    :param bot: объект бота
    :param content_template: текстовый шаблон уведомления
    :param time_of_day: метка времени (утро/день/вечер) для логирования
    """
    users = db.get_all_user_ids()
    tasks = []

    for user_id in users:
        try:
            # Получаем ID потока для пользователя
            thread_id = db.get_thread(user_id)

            # Генерируем текст уведомления
            text = await generator(content=content_template, user_id=user_id)

            # Добавляем задачу отправки сообщения
            tasks.append(
                bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
            )

        except Exception as e:
            print(f"Ошибка при подготовке сообщения для пользователя {user_id} ({time_of_day}): {e}")

    # Отправляем все сообщения параллельно
    try:
        await asyncio.gather(*tasks)
        print(f"Все {time_of_day} уведомления отправлены успешно.")
    except Exception as e:
        print(f"Ошибка при отправке {time_of_day} уведомлений: {e}")


# async def send_notifications(bot, content_template, time_of_day):
#     users = db.get_all_user_ids()
#
#     for user_id in users:
#         try:
#             thread_id = db.get_thread(user_id)
#             text = await generator(content=content_template, user_id=user_id)
#
#             # Отправка сообщений последовательно
#             await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
#             print(f"Уведомление отправлено пользователю {user_id} ({time_of_day})")
#             # await asyncio.sleep(10)
#
#         except Exception as e:
#             print(f"Ошибка при отправке сообщения для пользователя {user_id} ({time_of_day}): {e}")
#
#     print(f"Все {time_of_day} уведомления отправлены успешно.")


async def wait_for_thread(thread, retries=5, delay=2):
    """
    Ожидает освобождения потока.

    :param thread: объект потока
    :param retries: количество попыток
    :param delay: задержка между попытками
    :raises Exception: если поток остаётся занятым после всех попыток
    """
    for attempt in range(retries):
        if not thread.is_active:
            return
        print(f"Поток {thread.id} занят. Ожидание ({attempt + 1}/{retries})...")
        await asyncio.sleep(delay)
    raise Exception(f"Поток {thread.id} остаётся занятым после {retries} попыток.")


async def morning(bot):
    """
    Отправляет утренние уведомления.
    """
    content_template = '''
    Создай короткое утреннее уведомление, которое поддерживает пользователя и мотивирует на продуктивный день.
    Учитывай текущие транзиты, данные адаптивного интервью и тип личности.

    Инструкции:
    1. Приветствуй пользователя теплым и позитивным тоном.
    2. Напиши мотивирующую фразу длиной не более 1-2 предложений, чтобы поддержать его эмоциональное состояние и вдохновить на действие.
    3. Заверши сообщение предложением перейти к заданию на сегодня, когда пользователь будет готов.
    4. Сделай текст заряженным энергией, но лаконичным, понятным и легким.
    '''
    await send_notifications(bot, content_template, "утренних")


async def afternoon(bot):
    """
    Отправляет дневные уведомления.
    """
    content_template = '''
    Создай короткое дневное уведомление, чтобы поддержать пользователя в его стремлении оставаться продуктивным. Учитывай текущие транзиты, данные адаптивного интервью и тип личности.

    **Инструкции:**
    1. Начни с теплого приветствия.
    2. Включи вдохновляющую фразу, которая мотивирует пользователя продолжать выполнение своих планов.
    3. Заверши напоминанием о важности небольшого отдыха для сохранения энергии.
    4. Сделай текст лаконичным, вдохновляющим и поддерживающим.
    '''
    await send_notifications(bot, content_template, "дневных")


async def evening(bot):
    """
    Отправляет вечерние уведомления.
    """
    content_template = '''
    Создай короткое вечернее уведомление, чтобы поддержать пользователя в подведении итогов дня. Учитывай текущие транзиты, данные адаптивного интервью и тип личности.

    **Инструкции:**
    1. Поздравь пользователя с завершением продуктивного дня.
    2. Включи фразу, вдохновляющую на расслабление и отдых.
    3. Заверши напоминанием, что завтра будет новый день для достижения целей.
    4. Сделай текст уютным, успокаивающим и мотивирующим.
    '''
    await send_notifications(bot, content_template, "вечерних")


router = Router()


# Callback data factory
class StateCallbackData(CallbackData, prefix="state"):
    question: str
    response: str


# Периодическое уведомление
async def periodic_notification(bot):
    """
    Отправляет уведомление каждые три дня с вопросами для оценки текущего состояния.
    """
    users = db.get_all_user_ids()
    tasks = []

    for user_id in users:
        try:
            # Текст уведомления
            notification_text = '''
            Привет! Сегодня третий день вашего пути к цели. 
            Как вы себя чувствуете и что может помочь вам двигаться дальше? Ответьте на пару вопросов ниже.
            '''

            # Первый вопрос
            question_1 = "Как вы себя чувствуете сейчас?"
            keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Уверенно",
                                      callback_data=StateCallbackData(question="q1", response="confident").pack())],
                [InlineKeyboardButton(text="Спокойно",
                                      callback_data=StateCallbackData(question="q1", response="calm").pack())],
                [InlineKeyboardButton(text="Усталость",
                                      callback_data=StateCallbackData(question="q1", response="tired").pack())],
                [InlineKeyboardButton(text="Тревожность",
                                      callback_data=StateCallbackData(question="q1", response="anxious").pack())],
                [InlineKeyboardButton(text="Воодушевление",
                                      callback_data=StateCallbackData(question="q1", response="inspired").pack())],
            ])

            tasks.append(
                bot.send_message(chat_id=user_id, text=notification_text, reply_markup=keyboard_1, parse_mode='HTML')
            )
        except Exception as e:
            print(f"Ошибка при подготовке сообщения для пользователя {user_id} (трехдневное уведомление): {e}")

    # Отправляем все сообщения параллельно
    try:
        await asyncio.gather(*tasks)
        print("Трехдневное уведомление отправлено всем пользователям.")
    except Exception as e:
        print(f"Ошибка при отправке трехдневного уведомления: {e}")


# Обработка первого вопроса
@router.callback_query(lambda c: c.data.startswith("state:q1"))
async def handle_question_1(callback_query, state: FSMContext):
    """
    Вопрос 1: Как ты чувствуешь себя физически на данном этапе?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Как ты чувствуешь себя физически на данном этапе?"
    responses = {
        "good": "Хорошо",
        "neutral": "Нейтрально",
        "bad": "Плохо"
    }
    await state.update_data(вопрос_1=question_text, ответ_1=responses.get(response, "Неизвестно"))

    # Переход ко второму вопросу
    question_2 = "Что даёт тебе энергию или, наоборот, её отнимает?"
    keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Работа или задачи", callback_data="state:q2:work")],
        [InlineKeyboardButton(text="Отдых и время для себя", callback_data="state:q2:rest")],
        [InlineKeyboardButton(text="Окружение и события", callback_data="state:q2:environment")],
    ])

    await callback_query.message.edit_text(text=question_2, reply_markup=keyboard_2)


@router.callback_query(lambda c: c.data.startswith("state:q2"))
async def handle_question_2(callback_query, state: FSMContext):
    """
    Вопрос 2: Что даёт тебе энергию или, наоборот, её отнимает?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Что даёт тебе энергию или, наоборот, её отнимает?"
    responses = {
        "work": "Работа или задачи",
        "rest": "Отдых и время для себя",
        "environment": "Окружение и события"
    }
    await state.update_data(вопрос_2=question_text, ответ_2=responses.get(response, "Неизвестно"))

    # Переход к третьему вопросу
    question_3 = "Есть ли моменты в плане, которые вызывают сопротивление или чувство усталости?"
    keyboard_3 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, есть", callback_data="state:q3:yes")],
        [InlineKeyboardButton(text="Нет, всё нормально", callback_data="state:q3:no")],
    ])

    await callback_query.message.edit_text(text=question_3, reply_markup=keyboard_3)


@router.callback_query(lambda c: c.data.startswith("state:q3"))
async def handle_question_3(callback_query, state: FSMContext):
    """
    Вопрос 3: Есть ли моменты в плане, которые вызывают сопротивление или чувство усталости?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Есть ли моменты в плане, которые вызывают сопротивление или чувство усталости?"
    responses = {
        "yes": "Да, есть",
        "no": "Нет, всё нормально"
    }
    await state.update_data(вопрос_3=question_text, ответ_3=responses.get(response, "Неизвестно"))

    # Переход к четвёртому вопросу
    question_4 = "Что приносит радость и поддержку на этом этапе?"
    keyboard_4 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Успехи и результаты", callback_data="state:q4:success")],
        [InlineKeyboardButton(text="Поддержка близких", callback_data="state:q4:support")],
        [InlineKeyboardButton(text="Личное развитие", callback_data="state:q4:development")],
    ])

    await callback_query.message.edit_text(text=question_4, reply_markup=keyboard_4)


@router.callback_query(lambda c: c.data.startswith("state:q4"))
async def handle_question_4(callback_query, state: FSMContext):
    """
    Вопрос 4: Что приносит радость и поддержку на этом этапе?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Что приносит радость и поддержку на этом этапе?"
    responses = {
        "success": "Успехи и результаты",
        "support": "Поддержка близких",
        "development": "Личное развитие"
    }
    await state.update_data(вопрос_4=question_text, ответ_4=responses.get(response, "Неизвестно"))

    # Переход к пятому вопросу
    question_5 = "Сложно ли поддерживать уверенность в достижении цели? Как ты справляешься с этим?"
    keyboard_5 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, сложно", callback_data="state:q5:hard")],
        [InlineKeyboardButton(text="Нет, всё в порядке", callback_data="state:q5:ok")],
    ])

    await callback_query.message.edit_text(text=question_5, reply_markup=keyboard_5)


@router.callback_query(lambda c: c.data.startswith("state:q5"))
async def handle_question_5(callback_query, state: FSMContext):
    """
    Вопрос 5: Сложно ли поддерживать уверенность в достижении цели? Как ты справляешься с этим?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Сложно ли поддерживать уверенность в достижении цели? Как ты справляешься с этим?"
    responses = {
        "hard": "Да, сложно",
        "ok": "Нет, всё в порядке"
    }
    await state.update_data(вопрос_5=question_text, ответ_5=responses.get(response, "Неизвестно"))

    # Переход к шестому вопросу
    question_6 = "Нужно ли внести изменения в план, чтобы он лучше подходил к твоим текущим нуждам?"
    keyboard_6 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, нужно", callback_data="state:q6:yes")],
        [InlineKeyboardButton(text="Нет, всё устраивает", callback_data="state:q6:no")],
    ])

    await callback_query.message.edit_text(text=question_6, reply_markup=keyboard_6)


@router.callback_query(lambda c: c.data.startswith("state:q6"))
async def handle_question_6(callback_query, state: FSMContext):
    """
    Вопрос 6: Нужно ли внести изменения в план, чтобы он лучше подходил к твоим текущим нуждам?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Нужно ли внести изменения в план, чтобы он лучше подходил к твоим текущим нуждам?"
    responses = {
        "yes": "Да, нужно",
        "no": "Нет, всё устраивает"
    }
    await state.update_data(вопрос_6=question_text, ответ_6=responses.get(response, "Неизвестно"))

    # Переход к седьмому вопросу
    question_7 = "Чувствуешь ли ты в себе силы идти дальше, или нужна дополнительная поддержка?"
    keyboard_7 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Есть силы идти дальше", callback_data="state:q7:strong")],
        [InlineKeyboardButton(text="Нужна поддержка", callback_data="state:q7:support")],
    ])

    await callback_query.message.edit_text(text=question_7, reply_markup=keyboard_7)


@router.callback_query(lambda c: c.data.startswith("state:q7"))
async def handle_question_7(callback_query, state: FSMContext):
    """
    Вопрос 7: Чувствуешь ли ты в себе силы идти дальше, или нужна дополнительная поддержка?
    """
    user_id = callback_query.from_user.id
    response = callback_query.data.split(":")[2]  # Получаем значение ответа

    # Сохранение ответа
    question_text = "Чувствуешь ли ты в себе силы идти дальше, или нужна дополнительная поддержка?"
    responses = {
        "strong": "Есть силы идти дальше",
        "support": "Нужна поддержка"
    }
    await state.update_data(вопрос_7=question_text, ответ_7=responses.get(response, "Неизвестно"))

    # Завершение опроса и вывод всех данных
    data = await state.get_data()
    print(f"Сохраненные данные для пользователя {user_id}: {data}")

    await callback_query.message.answer("⏳ Пожалуйста, подождите, идет обработка данных...", parse_mode='HTML')
    final_message = await generator(user_id=callback_query.from_user.id, content=str(data))
    await callback_query.message.edit_text(text=final_message, reply_markup=None, parse_mode='HTML')


def start_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(morning, 'cron', hour=9, minute=0, args=[bot])  # Утренние уведомления в 8:00
    scheduler.add_job(afternoon, 'cron', hour=13, minute=0, args=[bot])  # Дневные уведомления в 13:00
    scheduler.add_job(evening, 'cron', hour=20, minute=0, args=[bot])  # Вечерние уведомления в 20:00
    scheduler.add_job(periodic_notification, 'interval', days=3, args=[bot])  # Уведомление каждые 3 дня
    # scheduler.add_job(morning, 'date', run_date=datetime.now() + timedelta(seconds=3), args=[bot])
    # scheduler.add_job(afternoon, 'date', run_date=datetime.now() + timedelta(seconds=50), args=[bot])
    # scheduler.add_job(evening, 'date', run_date=datetime.now() + timedelta(seconds=120), args=[bot])
    # scheduler.add_job(periodic_notification, 'date', run_date=datetime.now() + timedelta(seconds=160), args=[bot])

    scheduler.start()
