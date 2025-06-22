from datetime import datetime

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram import Router, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.keyboards as kb
from app.generators import *
from app.states import Form
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)



@router.callback_query(lambda c: c.data == 'astrology_no')
async def ast_no(callback_query: CallbackQuery):
    maybe = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔮 Да, давайте!', callback_data='astrology_yes')],
        [InlineKeyboardButton(text='🙅‍♂️ Нет, не хочу', callback_data='no_try_astrology')],
    ])
    await callback_query.message.answer(
        "🤔 А что если попробовать? Лишним точно не будет! \n\n"
        "🛡️ На войне с собой — все средства хороши. Может, всё-таки попробуете? ✨",
        reply_markup=maybe
    )


@router.callback_query(lambda c: c.data == 'astrology_yes')
async def ast_yes(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "📅 <b>Введите дату своего рождения</b> в формате <code>ДД.ММ.ГГГГ</code> 🔢",
        parse_mode="HTML"
    )
    await state.set_state(Form.birthday)

@router.message(Form.birthday)
async def process_date(message: Message, state: FSMContext):
    user_input = message.text.strip()
    if re.match(r'\d{2} \d{2} \d{4}', user_input):
        user_input = user_input.replace(' ', '.')

    possible_formats = [
        "%d.%m.%Y",  # дд.мм.гггг
        "%d-%m-%Y",  # дд-мм-гггг
        "%Y-%m-%d",  # гггг-мм-дд
        "%Y.%m.%d",  # гггг.мм.дд
        "%d/%m/%Y",  # дд/мм/гггг
        "%m/%d/%Y",  # мм/дд/гггг
    ]

    for date_format in possible_formats:
        try:
            date_obj = datetime.strptime(user_input, date_format)
            formatted_date = date_obj.strftime("%d.%m.%Y")
            await message.answer(
                f"📅 <b>Дата успешно распознана:</b> {formatted_date}\n\n"
                f"Теперь, пожалуйста, укажите <b>страну и город</b> вашего рождения 🌍",
                parse_mode='HTML'
            )
            await state.update_data(birth_day=formatted_date)
            await state.set_state(Form.place)
            return
        except ValueError:
            continue

    await message.answer(
        "❌ <b>Неверный формат даты.</b> Пожалуйста, введите дату в формате <i>дд.мм.гггг</i>.",
        parse_mode='HTML'
    )


@router.message(Form.place)
async def place(message: Message, state: FSMContext):
    place = message.text
    await state.update_data(place=place)
    await message.answer(
        '⏳ И наконец, укажите <b>время вашего рождения</b> 🕰️',
        parse_mode='HTML'
    )
    await state.set_state(Form.time)


@router.message(Form.time)
async def process_time(message: Message, state: FSMContext):
    user_input = message.text.strip()

    if re.match(r'\d{2} \d{2}', user_input):
        user_input = user_input.replace(' ', ':')
    elif re.match(r'\d{2}-\d{2}', user_input):
        user_input = user_input.replace('-', ':')

    possible_formats = [
        "%H:%M",  # чч:мм
        "%H.%M",  # чч.мм
    ]

    for time_format in possible_formats:
        try:
            time_obj = datetime.strptime(user_input, time_format)
            formatted_time = time_obj.strftime("%H:%M")
            await state.update_data(time=formatted_time)
            await message.answer(
                f"⏰ <b>Время успешно распознано:</b> {formatted_time} ✅\n\n",
                parse_mode='HTML'
            )
            await state.update_data(formatted_time=formatted_time)

            # await show_menu(message.from_user.id)

            data = await state.get_data()
            db.update_user_details(user_id=message.from_user.id, birth_day=data.get("birth_day"),
                                   birth_place=data.get("place"),
                                   birth_time=data.get("time"))


            await state.clear()

            return
        except ValueError:
            continue
    await message.answer(
        "❌ <b>Неверный формат времени.</b> Пожалуйста, введите время в формате <i>чч:мм</i>.",
        parse_mode='HTML'
    )

