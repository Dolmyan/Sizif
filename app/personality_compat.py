from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.generators import *
from app.handlers import show_menu, show_waiting_animation
from app.states import Personalityinput
from config import *
from personality_description import types
from database import BotDB

db = BotDB('sizif_mode.db')
router = Router()
bot = Bot(token=TG_TOKEN)
more_personality_compat = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Меню', callback_data='menu'),
    ],
    [
        InlineKeyboardButton(text='Узнать больше', callback_data='morepersonalitycompat'),
    ]
])

@router.callback_query(lambda c: c.data in ['personality_compat'])
async def personality_compat(callback_query: CallbackQuery, state: FSMContext):
    personality_type = db.get_personality_type(callback_query.from_user.id)
    partner_type=db.get_partner_personality_type(callback_query.from_user.id)
    if personality_type and partner_type:
        type_relation=None
        b=db.get_partner_details(callback_query.from_user.id)
        if b:
            type_relation=b['type_relation']
        a = await callback_query.message.answer("⏳ Пожалуйста, подождите, идет обработка данных...", parse_mode='HTML')
        id[0] = a.message_id
        response= await generate_personality_compat(personality_type, partner_type, type_relation)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=id[0])
        await callback_query.message.answer(f'Ваш тип личности: {personality_type}\n'
                                            f'Тип личности вашего партнера: {partner_type}\n\n'
                                            f'{response}', reply_markup=more_personality_compat,
                                            parse_mode='HTML')
    if not personality_type:
        await callback_query.message.answer(text='Ваш тип личности неизвестен. Предлагаем вам пройти наш тест. '
                                                 'Это не займет много времени', reply_markup=kb.gotest)
    elif not partner_type:
        await callback_query.message.answer(text='Тип личности вашего партнера неизвестен. '
                                                 'Если он уже проходил тест в нашем боте, '
                                                 'то используйте автозаполнение.'
                                                 'Если нет - введите его тип личности.',
                                            reply_markup=kb.personality_partner)


@router.callback_query(lambda c: c.data in ['morepersonalitycompat'])
async def morepersonality_compat(callback_query: CallbackQuery, state: FSMContext):
    a = await callback_query.message.answer("⏳ Пожалуйста, подождите", parse_mode='HTML')
    personality_type = db.get_personality_type(callback_query.from_user.id)
    partner_type=db.get_partner_personality_type(callback_query.from_user.id)
    request_task = asyncio.create_task(
        generator(
            user_id=callback_query.from_user.id,
            content=f'Мой тип личности:{personality_type}\n'
                    f'Тип личности моего партнера:{partner_type}\n'
                    f'Проанализируй и расскажи про нашу совместимость, подходим ли мы друг другу, '
                    f'наши сильные и слабые стороны'
        )
    )

    await show_waiting_animation(a, request_task)

    response = await request_task

    id[0] = a.message_id
    await callback_query.message.answer(text=f'{response}', parse_mode='HTML', reply_markup=kb.menu_button)



@router.callback_query(lambda c: c.data in ['input_personality'])
async def input_personality(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите тип личности партнера\n'
                                        'Например, ESTJ')
    await state.set_state(Personalityinput.personality)


@router.message(Personalityinput.personality)
async def input_personality(message: Message, state: FSMContext):
    personality = message.text.strip().upper()

    if personality in types:
        await message.answer('Тип личности успешно введен!')
        await show_menu(message.from_user.id)
        db.update_partner_personality_type(user_id=message.from_user.id, personality_type=personality)
