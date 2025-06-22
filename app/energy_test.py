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


class TestState(StatesGroup):
    question = State()


QUESTIONS = [
    "Как часто вы чувствуете усталость в течение дня?",
    "Как часто у вас болит голова или другие физические недомогания?",
    "Как часто вы тренируетесь или занимаетесь физической активностью?",
    "Как часто вы страдаете от бессонницы или нарушений сна?",
    "Как часто вы чувствуете боль в теле или другие физические симптомы стресса?",
    "Как часто у вас бывают простуды или другие заболевания?",
    "Как часто вы чувствуете слабость или отсутствие энергии?",
    "Как часто вы чувствуете головокружение или другие признаки плохого самочувствия?",
    "Как вы оцениваете качество своего сна?",
    "Как часто вы чувствуете головную боль или напряжение в глазах?",
    "Как часто вы чувствуете тревогу или стресс?",
    "Как вы оцениваете свою самооценку?",
    "Как часто вы чувствуете, что теряете интерес к жизни?",
    "Как часто вы чувствуете депрессию или уныние?",
    "Как вы справляетесь с негативными эмоциями?",
    "Как часто вы чувствуете внутреннюю пустоту или одиночество?",
    "Как часто вы переживаете о будущем?",
    "Как часто вы чувствуете поддержку от окружающих?",
    "Как вы оцениваете свои отношения с близкими людьми?",
    "Как часто вы чувствуете, что ваша работа или занятия приносят удовлетворение?",
    "Как часто вы испытываете стресс на работе или в учебе?",
    "Как часто вы испытываете конфликты с коллегами или окружающими людьми?",
    "Как часто вам удаётся наслаждаться обществом других людей?",
    "Как часто вы пользуетесь социальными сетями или интернетом в день?",
    "Как часто вы употребляете алкоголь?",
    "Как часто вы употребляете наркотические вещества или другие вредные вещества?",
    "Как часто вы смотрите телевизор или сериалы?",
    "Как часто вы занимаетесь физической активностью, например, спортом или прогулками?",
    "Как часто вы испытываете чувство голода или переедаете?",
    "Как часто вы испытываете внутреннее напряжение или беспокойство?"
]

ANSWERS = [
    ("Почти никогда", -3),
    ("Очень редко", -2),
    ("Иногда", -1),
    ("Редко", 0),
    ("Часто", +1),
    ("Очень часто", +2),
    ("Почти всегда", +3)
]

is_ast_working = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔮 Да, допускаю', callback_data='astrology_yes')],
    [InlineKeyboardButton(text='🙅‍♂️ Нет, не верю', callback_data='astrology_no')],
])

def generate_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="-3", callback_data="e-3"),
                InlineKeyboardButton(text="-1", callback_data="e-1"),
                InlineKeyboardButton(text="+1", callback_data="e1"),
                InlineKeyboardButton(text="+3", callback_data="e3"),
            ],
            [
                InlineKeyboardButton(text="-2", callback_data="e-2"),
                InlineKeyboardButton(text="0", callback_data="e0"),
                InlineKeyboardButton(text="+2", callback_data="e2"),
            ]
        ]
    )


@router.callback_query(lambda c: c.data in ['energy_test'])
async def menu(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(score=0, current_question=0)
    await send_question(callback_query.from_user.id, state)


async def send_question(chat_id: int, state: FSMContext):
    data = await state.get_data()
    current_question = data["current_question"]

    if current_question < len(QUESTIONS):
        question_text = f"<b>Вопрос {current_question + 1}/{len(QUESTIONS)}</b>\n⏳ <i>Оставшееся время: 10 секунд</i>\n\n{QUESTIONS[current_question]}"
        msg = await bot.send_message(chat_id, question_text, reply_markup=generate_keyboard(), parse_mode='HTML')

        await state.update_data(last_msg_id=msg.message_id)
        await asyncio.sleep(10)

        data = await state.get_data()
        if data.get("current_question"):
            if data["current_question"] == current_question:
                await handle_timeout(chat_id, state)
    else:
        await finish_test(chat_id, state)


async def handle_timeout(chat_id: int, state: FSMContext):
    data = await state.get_data()
    current_question = data["current_question"]
    score = data["score"]

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=data["last_msg_id"],
        text=f"⏳ <b>Время истекло!</b>\nВаш ответ автоматически засчитан как <i>нейтральный (0 баллов)</i>.",
        parse_mode='HTML',
    )

    await state.update_data(score=score + 0, current_question=current_question + 1)
    await send_question(chat_id, state)


@router.callback_query(F.data.in_([f"e{x[1]}" for x in ANSWERS]))
async def handle_answer(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data["current_question"]
    score = data["score"]

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"<b>Ответ принят!</b> ✅",
        parse_mode='HTML',
    )

    await state.update_data(score=score + int(callback_query.data[1:]), current_question=current_question + 1)
    await send_question(callback_query.message.chat.id, state)



async def finish_test(chat_id: int, state: FSMContext):
    data = await state.get_data()
    final_score = data["score"]
    avg_score = round(final_score / len(QUESTIONS), 2)

    level = ""
    if avg_score <= -2:
        level = "🔴 <b>Очень низкий уровень энергии</b>\nВы часто испытываете усталость и стресс."
    elif avg_score <= -1:
        level = "🟠 <b>Низкий уровень энергии</b>\nВам может не хватать сил в течение дня."
    elif avg_score <= 0:
        level = "🟡 <b>Средний уровень энергии</b>\nВыдерживаете нагрузки, но иногда устаёте."
    elif avg_score <= 1:
        level = "🟢 <b>Высокий уровень энергии</b>\nВы активны и полны сил!"
    else:
        level = "💚 <b>Очень высокий уровень энергии</b>\nВы заряжены и готовы к любым вызовам!"
    gotolife = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К следующему тесту', callback_data='life_test')],
    ])
    await bot.send_message(chat_id, f"<b>Тест завершён!</b>\n\n<b>Ваш средний балл:</b> {avg_score}\n\n{level}",
                           parse_mode='HTML',
                           reply_markup=gotolife)
    db.update_energy(user_id=chat_id, energy=final_score)
    await state.clear()




