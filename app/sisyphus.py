from datetime import datetime, timedelta

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.generators import *
from app.handlers import show_waiting_animation
from app.states import Form
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)

from sisyphus_questions import questions

trans = {
    "drink_water": "💧 Пить 2–3 л воды",
    "wake_earlier": "⏰ Просыпаться раньше",
    "exercise": "🏋️‍♂️ Спорт 3–4 раза в неделю",
    "read_books": "📖 Чтение книг",
    "goal_journal": "📓 Вести дневник целей",
    "time_management": "⏳ Тайм-менеджмент",
    "balanced_diet": "🥗 Сбалансированное питание",
    "no_procrastination": "🚀 Отказ от прокрастинации",
    "social_media_detox": "📵 Детокс от соцсетей",
    "meditation": "🧘‍♂️ Медитация/осознанность",
    "sleep_schedule": "🌙 Режим сна",
    "morning_exercise": "🤸‍♂️ Утренняя разминка",
    "weekly_review": "📊 Разбор успехов и неудач",
    "work_breaks": "🔄 Работа-перерывы",
    "track_expenses": "💰 Запись расходов",
    "clean_workspace": "🧹 Уборка рабочего места",
    "declutter": "🗑️ Чистка пространства",
    "fresh_air": "🌿 30 минут на воздухе",
    "no_gadgets": "📴 Без гаджетов перед сном",
    "less_caffeine_sugar": "☕ Ограничение кофе и сахара"
}

go_to_personality_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧩 Перейти к тесту', callback_data='personality_type')],
])


@router.callback_query(lambda c: c.data in ['sisyphus'])
async def sisyphus(callback_query: CallbackQuery, state: FSMContext):
    db.status_active(callback_query.from_user.id)
    if not db.get_info_up(callback_query.from_user.id).get('personality_type'):
        await callback_query.message.answer(
            "🔹 Чтобы бот работал корректно, нам нужно немного узнать о вас! \n\n"
            "✨ Для начала пройдите небольшой тест на определение вашего типа личности. "
            "Это поможет боту лучше адаптироваться под вас и давать более точные рекомендации.\n\n"
            "🚀 Готовы начать? Тогда нажмите кнопку ниже! 👇",
            reply_markup=go_to_personality_type
        )
    else:
        await callback_query.message.answer(
            text='Выберите действие 📌',
            reply_markup=kb.sisyphus_menu
        )


@router.callback_query(lambda c: c.data in ['today_task'])
async def today_task(callback_query: CallbackQuery, state: FSMContext):
    if db.get_sisyphus_date(callback_query.from_user.id):
        start = db.get_sisyphus_date(callback_query.from_user.id)
        today = datetime.now().strftime("%d-%m-%Y")

        # today='20-11-2024'

        start_date = datetime.strptime(start, '%d-%m-%Y')
        today_date = datetime.strptime(today, '%d-%m-%Y') + timedelta(days=1)

        day = (today_date - start_date).days
        a = await callback_query.message.answer("⏳ Пожалуйста, подождите, идет обработка данных...", parse_mode='HTML')

        response = await generator(user_id=callback_query.from_user.id, content=f'пришли план на день {day}')

        id[0] = a.message_id
        await callback_query.message.edit_text(text=f'{response}', parse_mode='HTML', reply_markup=kb.menu_button)
        await bot.delete_message(chat_id=callback_query.chat.id, message_id=id[0])
    else:
        await callback_query.message.answer(
            text='Что вас тревожит сейчас',
            reply_markup=kb.sisyphus
        )


@router.callback_query(lambda c: c.data in ['new_task'])
async def new_task(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text='Чем бы вы хотели заняться сейчас?',
        reply_markup=kb.sisyphus
    )


@router.callback_query(lambda c: c.data in [
    "drink_water", "wake_earlier", "exercise", "read_books", "goal_journal",
    "time_management", "balanced_diet", "no_procrastination", "social_media_detox",
    "meditation", "sleep_schedule", "morning_exercise", "weekly_review", "work_breaks",
    "track_expenses", "clean_workspace", "declutter", "fresh_air", "no_gadgets",
    "less_caffeine_sugar"
])
async def callback_generate_question(callback_query: CallbackQuery, state: FSMContext):
    theme = callback_query.data
    await state.update_data(sisyphus_theme=theme, current_question=0)  # Начинаем с 0-го вопроса
    await send_next_question(callback_query.message, state)


async def send_next_question(message, state: FSMContext):
    data = await state.get_data()
    theme = data.get('sisyphus_theme')
    question_number = data.get('current_question', 0)
    if question_number < len(questions[theme]):
        question_text = questions[theme][question_number]
        await message.answer(text=question_text, parse_mode='HTML')
        await state.update_data(
            {f'question{question_number + 1}': question_text, 'current_question': question_number + 1}
        )
    else:
        all_answers = []
        for i in range(1, len(questions[theme]) + 1):
            answer = data.get(f'answer{i}', 'Не был дан ответ')
            question = data.get(f'question{i}', 'Неизвестный вопрос')
            all_answers.append(f'Вопрос {i}: {question}\nОтвет: {answer}')

        all_answers_text = "\n\n".join(all_answers)

        # Получение данных пользователя из БД
        user_details = db.get_all_about(message.from_user.id)
        try:
            a = await message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')

            request_task = asyncio.create_task(
                generator(
                    user_id=message.from_user.id,
                    content='информация обо мне: '
                            f'{user_details}'
                            f'моя привычка: {trans[theme]}'
                            f'{all_answers_text}'
                            f'вся информация что ты '
                            f'будешь давать мне в дальнейшем '
                            f'должна быть максимально персонализирована. сейчас ты должен прислать'
                            f'мне теорию-мотивацию которая расскажет почему работа над '
                            f'моими привычками важна'
                )
            )

            await show_waiting_animation(a, request_task)

            response = await request_task

            id[0] = a.message_id
            button = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Получить задание', callback_data='get_task_sis'),
                ],
                [
                    InlineKeyboardButton(text='Меню', callback_data='menu'),
                ]
            ])
            await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=button)
            await bot.delete_message(chat_id=message.chat.id, message_id=id[0])
            db.sisyphus_active(message.from_user.id)
            await state.clear()
        except AttributeError:
            await message.answer('Мы приняли ваши вопросы, теперь заполните необходимую информацию.\n\n'
                                 'Введите вашу дату рождения')
            await state.set_state(Form.birthday)
    await state.set_state(Form.nexttt)


@router.message(Form.nexttt)
async def handle_question_response(message: Message, state: FSMContext):
    data = await state.get_data()
    question_number = data.get('current_question', 1)

    # Сохраняем ответ на текущий вопрос
    await state.update_data({f'answer{question_number}': message.text})

    # Переходим к следующему вопросу
    await send_next_question(message, state)


@router.callback_query(lambda c: c.data in ['get_task_sis'])
async def new_task(callback_query: CallbackQuery, state: FSMContext):
    a = await callback_query.message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')

    request_task = asyncio.create_task(
        generator(
            user_id=callback_query.from_user.id,
            content='учитывая всю информацию обо мне, сгенерируй одно задание на сегодня, '
                    'которое поможет мне бороться с моей привычкой '

        )
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id

    await callback_query.message.answer(text=f'{response}', parse_mode='HTML', reply_markup=kb.menu_button)
    db.update_tasks(callback_query.from_user.id, response)
    db.update_taskdate(callback_query.from_user.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=id[0])




