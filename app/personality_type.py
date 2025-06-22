from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.generators import *
from app.states import Form
from config import *
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)

from personality_description import *


zerototen = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='1'), InlineKeyboardButton(text='3', callback_data='3'),
     InlineKeyboardButton(text='5', callback_data='5'), InlineKeyboardButton(text='7', callback_data='7'),
     InlineKeyboardButton(text='9', callback_data='9')],
    [InlineKeyboardButton(text='2', callback_data='2'),
     InlineKeyboardButton(text='4', callback_data='4'), InlineKeyboardButton(text='6', callback_data='6'),
     InlineKeyboardButton(text='8', callback_data='8'), InlineKeyboardButton(text='10', callback_data='10')],
])


@router.callback_query(lambda c: c.data in ['personality_type'])
async def personality_type(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "🧠 <b>Чтобы определить твой тип личности, тебе придется ответить на некоторые вопросы.</b>\n\n"
        "📋 Тебе будут предложены различные высказывания. Если ты согласен — нажимай <b>🔟</b>, если не согласен — <b>1️⃣</b>.\n"
        "20 вопросов / 4 минуты",
        parse_mode='html'
    )
    await callback_query.message.answer(
        'Я люблю находиться в центре внимания и активно участвовать в разговоре.',
        reply_markup=zerototen
    )
    await state.set_state(Form.ei1)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.ei1)
async def ei2(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(ei=callback_query.data)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Мне комфортно в большом круге людей, и я заряжаюсь энергией от общения.',
        reply_markup=zerototen
    )
    await state.set_state(Form.ei2)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.ei2)
async def ei3(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ei = int(data['ei']) + int(callback_query.data)
    await state.update_data(ei=ei)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я быстро восстанавливаюсь после социального взаимодействия и люблю быть окруженным людьми.',
        reply_markup=zerototen
    )
    await state.set_state(Form.ei3)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.ei3)
async def ei4(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ei = int(data['ei']) + int(callback_query.data)
    await state.update_data(ei=ei)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я предпочитаю быть активным участником событий, а не молча наблюдать за происходящим.',
        reply_markup=zerototen
    )
    await state.set_state(Form.sn1)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.sn1)
async def sn2(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ei = int(data['ei']) + int(callback_query.data)
    await state.update_data(ei=ei)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я предпочитаю фокусироваться на фактах и деталях, чем на возможностях и абстрактных идеях.',
        reply_markup=zerototen
    )
    await state.set_state(Form.sn2)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.sn2)
async def sn3(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sn = int(callback_query.data)
    await state.update_data(sn=sn)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Когда я работаю над задачей, мне важнее следовать проверенным методам, чем искать новые пути.',
        reply_markup=zerototen
    )
    await state.set_state(Form.sn3)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.sn3)
async def sn4(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sn = int(data['sn']) + int(callback_query.data)
    await state.update_data(sn=sn)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я больше сосредотачиваюсь на том, что происходит сейчас, чем на том, что может произойти в будущем.',
        reply_markup=zerototen
    )
    await state.set_state(Form.sn4)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.sn4)
async def sn5(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sn = int(data['sn']) + int(callback_query.data)
    await state.update_data(sn=sn)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Мне проще опираться на прошлый опыт и конкретные факты, чем на абстрактные идеи и догадки.',
        reply_markup=zerototen
    )
    await state.set_state(Form.tf1)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.tf1)
async def tf2(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sn = int(data['sn']) + int(callback_query.data)
    await state.update_data(sn=sn)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='При принятии решений я чаще руководствуюсь логикой и объективностью, чем чувствами и эмоциями.',
        reply_markup=zerototen
    )
    await state.set_state(Form.tf2)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.tf2)
async def tf3(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tf = int(callback_query.data)
    await state.update_data(tf=tf)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='В конфликтах для меня важнее быть объективным и справедливым, чем заботиться о гармонии и чувствах других.',
        reply_markup=zerototen
    )
    await state.set_state(Form.tf3)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.tf3)
async def tf4(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tf = int(data['tf']) + int(callback_query.data)
    await state.update_data(tf=tf)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я стараюсь избегать эмоциональных обсуждений и предпочитаю анализировать ситуацию с холодной головой.',
        reply_markup=zerototen
    )
    await state.set_state(Form.tf4)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.tf4)
async def jp1(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tf = int(data['tf']) + int(callback_query.data)
    await state.update_data(tf=tf)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я принимаю решения, ориентируясь на объективные критерии и логику, даже если это может вызвать негативные эмоции у других.',
        reply_markup=zerototen
    )
    await state.set_state(Form.jp1)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.jp1)
async def jp2(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tf = int(data['tf']) + int(callback_query.data)
    await state.update_data(tf=tf)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я предпочитаю заранее планировать и организовывать свою работу, чтобы всё было под контролем.',
        reply_markup=zerototen
    )
    await state.set_state(Form.jp2)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.jp2)
async def jp3(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jp = int(callback_query.data)
    await state.update_data(jp=jp)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Мне комфортнее, когда у меня есть чёткий план действий и расписание, чем когда всё решается спонтанно.',
        reply_markup=zerototen
    )
    await state.set_state(Form.jp3)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.jp3)
async def jp4(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jp = int(data['jp']) + int(callback_query.data)
    await state.update_data(jp=jp)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Я предпочитаю завершать начатые дела как можно быстрее, чем оставлять их на последний момент.',
        reply_markup=zerototen
    )
    await state.set_state(Form.jp4)


@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.jp4)
async def jp5(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jp = int(data['jp']) + int(callback_query.data)
    await state.update_data(jp=jp)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text='Мне нравится, когда у меня есть свобода выбирать, чем заняться и в каком порядке, а не следовать строго установленному плану.',
        reply_markup=zerototen
    )
    await state.set_state(Form.jp5)



@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], Form.jp5)
async def jp1(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    jp = int(data['jp']) + int(callback_query.data)
    await state.update_data(jp=jp)
    data = await state.get_data()
    ei = 'I' if int(data['ei']) <= 25 else 'E'
    sn = 'N' if int(data['sn']) <= 25 else 'S'
    tf = 'F' if int(data['tf']) <= 25 else 'T'
    jp = 'P' if int(data['jp']) <= 25 else 'J'
    descriptions = {
        "ESTJ": ESTJ_description,
        "INFP": INFP_description,
        "INTJ": INTJ_description,
        "ESFP": ESFP_description,
        "ENTP": ENTP_description,
        "ISFJ": ISFJ_description,
        "INFJ": INFJ_description,
        "ISTJ": ISTJ_description,
        "ENFJ": ENFJ_description,
        "ISTP": ISTP_description,
        "ISFP": ISFP_description,
        "ESTP": ESTP_description,
        "ENTJ": ENTJ_description,
        "ENFP": ENFP_description,
        "INTP": INTP_description,
        "ESFJ": ESFJ_description,
    }
    type=f'{ei}{sn}{tf}{jp}'
    await callback_query.message.edit_text(text=descriptions[type], parse_mode='HTML', reply_markup=kb.menu_button_more_personality)
    db.update_personality_type(user_id=callback_query.from_user.id, personality_type=type)


@router.callback_query(lambda c: c.data in ['morepersonality'])
async def more_personality(callback_query: CallbackQuery, state: FSMContext):
    a = await callback_query.message.answer("⏳ Пожалуйста, подождите, идет обработка данных...", parse_mode='HTML')
    id[0] = a.message_id
    personality_type = db.get_personality_type(callback_query.from_user.id)
    response=await generate_more_personality(personality_type)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=id[0])
    await callback_query.message.answer(text=response, parse_mode='HTML', reply_markup=kb.menu_button)