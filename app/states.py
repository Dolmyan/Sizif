from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    nexttt = State()
    birthday = State()
    place = State()
    time = State()
    type_relation = State()
    partner_username = State()
    ei1 = State()
    ei2 = State()
    ei3 = State()
    ei4 = State()
    sn1 = State()
    sn2 = State()
    sn3 = State()
    sn4 = State()

    tf1 = State()
    tf2 = State()
    tf3 = State()
    tf4 = State()

    jp1 = State()
    jp2 = State()
    jp3 = State()
    jp4 = State()
    jp5 = State()

    test = State()
    dream = State()
    motivation = State()
    five_why = State()

    waiting_for_want = State()  # Ожидаем первый ответ
    waiting_for_why1 = State()  # Ожидаем первый вопрос "Почему?"
    waiting_for_why2 = State()  # Ожидаем второй вопрос "Почему?"
    waiting_for_why3 = State()  # Ожидаем третий вопрос "Почему?"
    waiting_for_why4 = State()  # Ожидаем четвёртый вопрос "Почему?"
    waiting_for_why5 = State()  # Ожидаем пятый вопрос "Почему?"


class Partnerinput(StatesGroup):
    birthday = State()
    place = State()
    time = State()
    type_relation = State()
    partner_username = State()


class Personalityinput(StatesGroup):
    username = State()
    personality = State()


class Sisyphus(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()
    question6 = State()
    question7 = State()
    question8 = State()
    question9 = State()


class Todo(StatesGroup):
    task = State()
    awaiting_task = State()
    time = State()
    description = State()
    reminder = State()


class Up(StatesGroup):
    partner_info = State()
