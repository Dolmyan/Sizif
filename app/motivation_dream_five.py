from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.keyboards as kb
from app.generators import *
from app.handlers import show_waiting_animation
from app.states import Form
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)


@router.message(Form.motivation)
async def cmd_start(message: Message, state: FSMContext):
    motivation = message.text
    db.update_motivation(user_id=message.from_user.id, motivation=motivation)
    await message.answer(
        text='<b>А теперь расскажи о своей мечте 💫</b>\nО чём ты мечтаешь? Напиши 2–3 желания, которые греют душу 💖',
        parse_mode="HTML"
    )
    await state.set_state(Form.dream)


@router.message(Form.dream)
async def cmd_start(message: Message, state: FSMContext):
    dream = message.text
    db.update_dream(user_id=message.from_user.id, dream=dream)
    await message.answer(
        text='<b>А теперь давай начнём тест "5 Почему" 🔍</b>\nНапиши, <i>чего ты хочешь?</i> (например, «Хочу много денег»).',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_want)


@router.message(Form.waiting_for_want)
async def ask_first_question(message: Message, state: FSMContext):
    user_want = message.text
    await state.update_data(first_want=user_want)
    await message.answer(
        text='<i>Почему это является твоей целью?</i>',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_why1)


@router.message(Form.waiting_for_why1)
async def ask_second_question(message: Message, state: FSMContext):
    user_answer_why1 = message.text
    data = await state.get_data()
    user_want = data.get('first_want')
    await state.update_data(answer_why1=user_answer_why1)
    await message.answer(
        text=f'Ты сказал, что хочешь {user_want}. <i>Почему это важно для тебя?</i>',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_why2)


@router.message(Form.waiting_for_why2)
async def ask_third_question(message: Message, state: FSMContext):
    user_answer_why2 = message.text
    data = await state.get_data()
    await state.update_data(answer_why2=user_answer_why2)
    await message.answer(
        text=f'Ты сказал, что {user_answer_why2} важно. <i>Как это влияет на твою жизнь?</i>?',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_why3)


@router.message(Form.waiting_for_why3)
async def ask_fourth_question(message: Message, state: FSMContext):
    user_answer_why3 = message.text
    data = await state.get_data()
    await state.update_data(answer_why3=user_answer_why3)
    await message.answer(
        text=f'Ты сказал, что {user_answer_why3} влияет на твою жизнь. <i>Как это связано с твоими долгосрочными целями?</i>',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_why4)


@router.message(Form.waiting_for_why4)
async def ask_fifth_question(message: Message, state: FSMContext):
    user_answer_why4 = message.text
    data = await state.get_data()
    await state.update_data(answer_why4=user_answer_why4)
    await message.answer(
        text=f'Ты сказал, что {user_answer_why4} важно для твоих целей. <i>Почему это так важно для тебя лично?</i>',
        parse_mode="HTML"
    )
    await state.set_state(Form.waiting_for_why5)


@router.message(Form.waiting_for_why5)
async def finalize_test(message: Message, state: FSMContext):
    user_answer_why5 = message.text
    data = await state.get_data()
    await state.update_data(answer_why5=user_answer_why5)

    # Собираем все ответы
    answers = [
        data.get('first_want'),
        data.get('answer_why1'),
        data.get('answer_why2'),
        data.get('answer_why3'),
        data.get('answer_why4'),
        user_answer_why5
    ]
    # Завершаем тест

    a = await message.answer("⏳ Пожалуйста, подождите, формируем вашу истинную мечту", parse_mode='HTML')

    request_task = asyncio.create_task(
        generator(
            user_id=message.from_user.id,
            content=f'Проанализируй мои ответы и четко сформулируй - что является моей истинной мечтой.'
                    f'ответ должен быть максимально кратким'
             f'Чего ты хочешь? {answers[0]}\n'
             f'Почему это важно? {answers[1]}\n'
             f'Как это влияет на твою жизнь? {answers[2]}\n'
             f'Как это связано с твоими долгосрочными целями? {answers[3]}\n'
             f'Почему это так важно для тебя лично? {answers[4]} {answers[5]}\n\n'

        )
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id
    energy_test_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🧩 Перейти к следующему тесту', callback_data='energy_test')],
    ])
    await message.answer(text=f'{response}', parse_mode='HTML', reply_markup=energy_test_button)
    await bot.delete_message(chat_id=message.from_user.id, message_id=id[0])

    await state.clear()
