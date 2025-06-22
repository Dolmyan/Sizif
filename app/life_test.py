from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
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
bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


class SurveyState(StatesGroup):
    question = State()


QUESTIONS = [
    "Во сколько вы обычно просыпаетесь по будням?",
    "А во сколько ложитесь спать?",
    "Какой у вас график работы?",
    "Сколько часов в день вы работаете в среднем?",
    "Насколько вам нравится ваша работа? (1-10)",
    "У вас есть дети?",
    "С кем вы живёте?",
    "Как часто вы проводите время с друзьями?",
    "Насколько вы довольны своим окружением? (1-10)",
    "Сколько у вас свободного времени в будний день?",
    "А в выходной?",
    "Как вы обычно проводите свободное время? (можно выбрать несколько)",
    "У вас есть хобби?",
    "Как часто вы занимаетесь хобби?",
    "Вы следите за питанием?",
    "Сколько раз в неделю занимаетесь спортом или активностью?",
    "Насколько у вас высокий уровень стресса? (1-10)",
    "Какой у вас уровень дохода по вашему мнению?",
    "Вы довольны своей финансовой ситуацией? (1-10)",
    "Есть ли у вас планы по смене работы или росту в карьере?",
    "Какая сфера жизни вас беспокоит больше всего?",
    "Где бы вы хотели оказаться через 5 лет?",
    "Вы чувствуете себя реализованным человеком? (1-10)",
    "Если бы у вас было дополнительно 2 часа в день, на что бы вы их потратили? (можно выбрать несколько)",
    "Насколько вы довольны своей жизнью в целом? (1-10)",
]

ANSWERS = {
    0: ["До 6:00", "6:00 – 7:00", "7:00 – 8:00", "Позже 8:00"],
    1: ["До 22:00", "22:00 – 00:00", "00:00 – 02:00", "Позже 02:00"],
    2: ["5/2", "Гибкий", "Удалёнка", "В офисе", "Свой бизнес", "Другое"],
    3: ["Менее 4 часов", "4–6 часов", "6–8 часов", "Более 8 часов"],
    4: [str(i) for i in range(1, 11)],
    5: ["Нет", "Да, 1 ребенок", "Да, 2 и более"],
    6: ["Один", "С партнёром", "С родителями", "С друзьями/соседями"],
    7: ["Почти каждый день", "Несколько раз в неделю", "Раз в неделю", "Реже, чем раз в неделю"],
    8: [str(i) for i in range(1, 11)],
    9: ["Практически нет", "До 1 часа", "1–3 часа", "Более 3 часов"],
    10: ["Практически нет", "До 3 часов", "3–6 часов", "Более 6 часов"],
    11: ["Социальные сети", "Спорт", "Чтение", "Хобби", "Общение", "Отдых"],
    12: ["Нет", "Да, одно", "Да, несколько"],
    13: ["Каждый день", "Несколько раз в неделю", "Раз в неделю", "Редко"],
    14: ["Да, строго", "В целом стараюсь", "Нет, ем что угодно"],
    15: ["0", "1–2 раза", "3–4 раза", "5 и более раз"],
    16: [str(i) for i in range(1, 11)],
    17: ["Ниже среднего", "Средний", "Выше среднего", "Высокий"],
    18: [str(i) for i in range(1, 11)],
    19: ["Устраивает", "Возможно", "Смена", "Бизнес"],
    20: ["Карьера", "Здоровье", "Отношения", "Саморазвитие", "Эмоции"],
    21: ["Рост в карьере", "Смена сферы", "Свой бизнес", "Счастливая жизнь"],
    22: [str(i) for i in range(1, 11)],
    23: ["Спорт", "Хобби", "Обучение", "Общение", "Отдых"],
    24: [str(i) for i in range(1, 11)],
}


def clean_callback_data(text):
    return re.sub(r"[^a-zа-яё0-9_]", "", text.lower().replace(" ", "_"))[:30]


def generate_keyboard(question_index):
    buttons = [InlineKeyboardButton(text=option, callback_data=clean_callback_data(option)) for option in
               ANSWERS[question_index]]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(lambda c: c.data in ['life_test'])
async def menu(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(answers={})
    await state.update_data(current_question=0)
    await send_question(callback_query.from_user.id, state)


async def send_question(chat_id: int, state: FSMContext):
    data = await state.get_data()
    current_question = data.get("current_question", 0)
    last_msg_id = data.get("last_msg_id")

    if current_question < len(QUESTIONS):
        question_text = f"<b>Вопрос {current_question + 1}/{len(QUESTIONS)}</b>\n\n{QUESTIONS[current_question]}"

        if last_msg_id:
            # Редактируем предыдущее сообщение
            try:
                await bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text=question_text,
                                            reply_markup=generate_keyboard(current_question), parse_mode="HTML")
            except Exception:
                # Если сообщение не найдено (например, было удалено), отправляем новое
                msg = await bot.send_message(chat_id, question_text, reply_markup=generate_keyboard(current_question),
                                             parse_mode="HTML")
                await state.update_data(last_msg_id=msg.message_id)
        else:
            # Отправляем новое сообщение, если last_msg_id отсутствует
            msg = await bot.send_message(chat_id, question_text, reply_markup=generate_keyboard(current_question),
                                         parse_mode="HTML")
            await state.update_data(last_msg_id=msg.message_id)
    else:
        await finish_survey(chat_id, state)


@router.callback_query(F.data)
async def handle_answer(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data.get("current_question", 0)  # Безопасное получение значения
    answers = data.get("answers", {})

    # Проверяем, что текущий вопрос не выходит за границы списка
    if current_question >= len(QUESTIONS):
        await finish_survey(callback_query.message.chat.id, state)
        return  # Прерываем выполнение, чтобы избежать IndexError

    # Сохраняем ответ пользователя
    answers[QUESTIONS[current_question]] = callback_query.data

    # Показываем уведомление (исправлен вызов callback_query.answer)
    await callback_query.answer("Ответ сохранён! ✅")

    await state.update_data(answers=answers, current_question=current_question + 1)
    await send_question(callback_query.message.chat.id, state)


def format_time(time_str):
    """Преобразует '600__700' в '06:00–07:00'"""
    try:
        parts = time_str.split("__")
        formatted_parts = [f"{p[:-2]}:{p[-2:]}" for p in parts]
        return "–".join(formatted_parts)
    except:
        return time_str  # Если формат неожиданно другой, вернуть как есть



async def finish_survey(chat_id: int, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")  # Получаем ID последнего сообщения

    # Удаляем последнее сообщение с вопросом, если оно есть
    if last_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
        except Exception:
            pass  # Игнорируем ошибки, если сообщение уже удалено


    data = await state.get_data()
    answers = data["answers"]

    wake_time = format_time(answers.get("Во сколько вы обычно просыпаетесь по будням?", "Не указано"))
    sleep_time = format_time(answers.get("А во сколько ложитесь спать?", "Не указано"))
    regime = f"просыпаюсь {wake_time} : засыпаю {sleep_time}" if wake_time and sleep_time else "Не указано"

    formatted_results = f"""
{regime}
График: {answers.get("Какой у вас график работы?", "Не указано")}
Работа: {answers.get("Сколько часов в день вы работаете в среднем?", "Не указано")} ч
Удовл_работой: {answers.get("Насколько вам нравится ваша работа? (1-10)", "Не указано")}/10
Дети: {answers.get("У вас есть дети?", "Не указано")}
Живёт: {answers.get("С кем вы живёте?", "Не указано")}
Друзья: {answers.get("Как часто вы проводите время с друзьями?", "Не указано")}
Окружение: {answers.get("Насколько вы довольны своим окружением? (1-10)", "Не указано")}/10
Св. время (будни): {answers.get("Сколько у вас свободного времени в будний день?", "Не указано")}
Св. время (выходные): {answers.get("А в выходной?", "Не указано")}
Досуг: {answers.get("Как вы обычно проводите свободное время? (можно выбрать несколько)", "Не указано")}
Хобби: {answers.get("У вас есть хобби?", "Не указано")}
Частота хобби: {answers.get("Как часто вы занимаетесь хобби?", "Не указано")}
Питание: {answers.get("Вы следите за питанием?", "Не указано")}
Спорт: {answers.get("Сколько раз в неделю занимаетесь спортом или активностью?", "Не указано")} раз
Стресс: {answers.get("Насколько у вас высокий уровень стресса? (1-10)", "Не указано")}/10
Доход: {answers.get("Какой у вас уровень дохода по вашему мнению?", "Не указано")}
Финансы: {answers.get("Вы довольны своей финансовой ситуацией? (1-10)", "Не указано")}/10
Карьера: {answers.get("Есть ли у вас планы по смене работы или росту в карьере?", "Не указано")}
Приоритет: {answers.get("Какая сфера жизни вас беспокоит больше всего?", "Не указано")}
Цели (5 лет): {answers.get("Где бы вы хотели оказаться через 5 лет?", "Не указано")}
Самореализация: {answers.get("Вы чувствуете себя реализованным человеком? (1-10)", "Не указано")}/10
Доп. 2 часа в день: {answers.get("Если бы у вас было дополнительно 2 часа в день, на что бы вы их потратили? (можно выбрать несколько)", "Не указано")}
Удовл_жизнью: {answers.get("Насколько вы довольны своей жизнью в целом? (1-10)", "Не указано")}/10"""
    db.update_about(user_id=chat_id, about=formatted_results)
    await state.clear()

    # await bot.send_message(chat_id, formatted_results, parse_mode="HTML")
    await bot.send_message(
        chat_id,
        "✨ <b>Изменения начинаются тут.</b>\n"
        "Готовься приступить к <b>кардинальному</b> изменению в жизни! 💪🔥",
        parse_mode="HTML"
    )

    await asyncio.sleep(3)

    await bot.send_message(
        text=(
            "🚀 <b>Двигайся к целям постепенно — становись лучше на 1% каждый день!</b>\n\n"
            "📌 <b>Как это работает:</b>\n"
            "✅ Выбери <b>привычку</b> — этого достаточно, чтобы уже начать меняться.\n"
            "✅ Мы используем <b>4-недельную программу</b>, потому что <b>21 день</b> слишком интенсивен, а такой формат помогает <b>закрепить результаты</b>.\n"
            "✅ Повторяй шаги <b>каждый день</b>, добавляя новые привычки по мере готовности!\n\n"
            "📅 <b>Начни прямо сейчас</b>, чтобы видеть первые изменения уже через <b>4 недели!</b> "
        ),
        chat_id=chat_id,
        parse_mode="HTML",
        reply_markup=kb.sisyphus
    )


