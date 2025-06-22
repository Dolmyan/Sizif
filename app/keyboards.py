from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

sex = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мужчина', callback_data='male')],
    [InlineKeyboardButton(text='Женщина', callback_data='female')],
])

menu = InlineKeyboardMarkup(inline_keyboard=[

    [InlineKeyboardButton(text='✅ ToDo (простой список задач)', callback_data='todo_todo')],
    [InlineKeyboardButton(text='🧩 Декомпозитор (разбить план)', callback_data='todo_decomposer')],
    [InlineKeyboardButton(text='⏰ Планировщик (распределить задачи)', callback_data='todo_scheduler')],
    [
        InlineKeyboardButton(text='🛠️ Сизиф (яЯ) 💪', callback_data='sisyphus')
    ],

    [
        InlineKeyboardButton(text='🔍 Профиль', callback_data='profile'),
    ],
])

menu_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Меню', callback_data='menu'),
    ]
])

menu_button_more_personality = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='К следующему тесту', callback_data='energy_test'),
    ],
    [
        InlineKeyboardButton(text='Узнать больше', callback_data='morepersonality'),
    ]
])

data_partner = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, использовать автозаполнение', callback_data='auto_partner')],
    [InlineKeyboardButton(text='Нет, ввести данные вручную', callback_data='input_partner_data')],
])

data_partner_error = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести другой username', callback_data='auto_partner')],
    [InlineKeyboardButton(text='Ввести данные вручную', callback_data='input_partner_data')],
])

data_partner_confirmation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, все верно', callback_data='natal_compat')],
    [InlineKeyboardButton(text='Заполнить данные самостоятельно', callback_data='input_partner_data')],
])

registration = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Регистрация', callback_data='registration'),
    ]
])

gotest = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Пройти тест', callback_data='personality_type'),
    ]
])

personality_partner = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, использовать автозаполнение', callback_data='auto_personality')],
    [InlineKeyboardButton(text='Нет, ввести данные вручную', callback_data='input_personality')],
])

personality_error = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввести другой username', callback_data='auto_personality')],
    [InlineKeyboardButton(text='Ввести данные вручную', callback_data='input_personality')],
])

personality_confirmation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, все верно', callback_data='personality_compat')],
    [InlineKeyboardButton(text='Заполнить данные самостоятельно', callback_data='input_personality')],
])


sisyphus = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💧 Пить 2–3 л воды', callback_data='drink_water')],
    [InlineKeyboardButton(text='⏰ Просыпаться раньше', callback_data='wake_earlier')],
    [InlineKeyboardButton(text='🏋️‍♂️ Спорт 3–4 раза в неделю', callback_data='exercise')],
    [InlineKeyboardButton(text='📖 Чтение книг', callback_data='read_books')],
    [InlineKeyboardButton(text='📓 Вести дневник целей', callback_data='goal_journal')],
    [InlineKeyboardButton(text='⏳ Тайм-менеджмент', callback_data='time_management')],
    [InlineKeyboardButton(text='🥗 Сбалансированное питание', callback_data='balanced_diet')],
    [InlineKeyboardButton(text='🚀 Отказ от прокрастинации', callback_data='no_procrastination')],
    [InlineKeyboardButton(text='📵 Детокс от соцсетей', callback_data='social_media_detox')],
    [InlineKeyboardButton(text='🧘‍♂️ Медитация/осознанность', callback_data='meditation')],
    [InlineKeyboardButton(text='🌙 Режим сна', callback_data='sleep_schedule')],
    [InlineKeyboardButton(text='🤸‍♂️ Утренняя разминка', callback_data='morning_exercise')],
    [InlineKeyboardButton(text='📊 Разбор успехов и неудач', callback_data='weekly_review')],
    [InlineKeyboardButton(text='🔄 Работа-перерывы', callback_data='work_breaks')],
    [InlineKeyboardButton(text='💰 Запись расходов', callback_data='track_expenses')],
    [InlineKeyboardButton(text='🧹 Уборка рабочего места', callback_data='clean_workspace')],
    [InlineKeyboardButton(text='🗑️ Чистка пространства', callback_data='declutter')],
    [InlineKeyboardButton(text='🌿 30 минут на воздухе', callback_data='fresh_air')],
    [InlineKeyboardButton(text='📴 Без гаджетов перед сном', callback_data='no_gadgets')],
    [InlineKeyboardButton(text='☕ Ограничение кофе и сахара', callback_data='less_caffeine_sugar')],
])

sisyphus_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='🚀 Начать новое направление', callback_data='new_task')
    ],
    [
        InlineKeyboardButton(text='📅 Просмотреть сегодняшнее задание', callback_data='today_task')
    ],

    [InlineKeyboardButton(text='🔙 Назад', callback_data='menu')],

])