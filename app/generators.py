import re
import time

import openai
import httpx
from openai import AssistantEventHandler, AsyncOpenAI
from typing_extensions import override
import asyncio

from config import AI_TOKEN#, PROXY
import logging

from database import BotDB

# Логирование для диагностики
logging.basicConfig(level=logging.INFO)

cached_assistant_id = None

db = BotDB('sizif_mode.db')


# Прокси-сервер
def res(response):
    response = re.sub(r'###(.*?)###', r'<b>\1</b>', response)
    response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
    response = re.sub(r'####(.*?)', r'*\1*', response)
    response = re.sub(r'###(.*?)', r'\1', response)
    return response


# Настройка прокси для httpx
# proxies = {
#     "http://": PROXY,
#     "https://": PROXY
# }
#
# # Инициализация клиента OpenAI с использованием прокси
# client = AsyncOpenAI(api_key=AI_TOKEN,
#                      http_client=httpx.AsyncClient(
#                          proxies=proxies,
#                          transport=httpx.HTTPTransport(local_address="0.0.0.0")
#                      ))
import httpx
from openai import AsyncOpenAI




client = AsyncOpenAI(
    api_key=AI_TOKEN,
    http_client=httpx.AsyncClient(


    )
)




async def get_assistant():
    global cached_assistant_id
    if cached_assistant_id:
        return cached_assistant_id

    try:
        # Попытка получить список ассистентов
        assistants_list = await client.beta.assistants.list()
        for existing_assistant in assistants_list.data:
            if existing_assistant.name == "Lovele":
                cached_assistant_id = existing_assistant.id
                logging.info(f"Используется существующий ассистент с ID: {cached_assistant_id}")
                return cached_assistant_id

        # Создание ассистента (если необходимо)
        # assistant = await client.beta.assistants.create(name="Lovele")
        # cached_assistant_id = assistant.id
        logging.info(f"Создан новый ассистент с ID: {cached_assistant_id}")
        return cached_assistant_id
    except openai.APIConnectionError as e:
        logging.error(f"Ошибка подключения к API OpenAI: {e}")
        raise e




async def get_thread_content(thread_id):
    # Получаем все сообщения из потока
    messages_response = await client.beta.threads.messages.list(thread_id=thread_id)

    extracted_messages = []
    # Проходим по каждому сообщению
    for message in messages_response.data:
        # Проверяем наличие контента
        if hasattr(message, 'content') and message.content:
            for block in message.content:
                # Проверяем, содержит ли блок текст
                if hasattr(block, 'text') and hasattr(block.text, 'value'):
                    extracted_messages.append({
                        'role': message.role,  # Роль: 'user' или 'assistant'
                        'text': block.text.value  # Текст сообщения
                    })

    return extracted_messages


# Определение асинхронной функции для работы с ассистентом
async def first_request(date, place, birth_time):
    # Проверка существования ассистента
    assistants_list = await client.beta.assistants.list()
    assistant = None

    for existing_assistant in assistants_list.data:
        if existing_assistant.name == "Lovele":
            assistant = existing_assistant
            break

    if assistant:
        print(f"Используется существующий ассистент с ID: {assistant.id}")
    else:
        print(f"Создан новый ассистент с ID: {assistant.id}")

    # Создание новой нити для диалога
    thread = await client.beta.threads.create()
    # Добавление сообщения от пользователя в нить
    response = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Рассчитай мою натальную карту и дай мне большой и развернутый ответ. "
                "Используй западный метод"
                f"Моя дата рождения: {date}"
                f"Место моего рождения: {place}"
                f"Время моего рождения: {birth_time}"  # Текст сообщения от пользователя
    )

    # Запуск ассистента для обработки сообщения
    run_response = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,  # Использование корректного ID ассистента
    )

    # Проверка статуса до завершения выполнения
    status = run_response.status
    while status != 'completed':
        run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread.id)
        status = run_status.status

        if status == 'failed':
            print("Запуск завершился с ошибкой")
            return

        if status == 'completed':
            break

        # Ожидание перед следующей проверкой статуса
        time.sleep(5)

    # Получение всех сообщений в нити
    messages_response = await client.beta.threads.messages.list(thread_id=thread.id)

    if messages_response.data:
        text = res(messages_response.data[0].content[0].text.value)
        return text
    else:
        print("Сообщений нет.")


async def generate_natal_compat(date, place, birth_time, partner_date, partner_place, partner_birth_time,
                                type_relation):
    # Проверка существования ассистента
    assistants_list = await client.beta.assistants.list()
    assistant = None

    for existing_assistant in assistants_list.data:
        if existing_assistant.name == "Lovele":
            assistant = existing_assistant
            break

    if assistant:
        print(f"Используется существующий ассистент с ID: {assistant.id}")
    else:
        print(f"Создан новый ассистент с ID: {assistant.id}")

    # Создание новой нити для диалога
    thread = await client.beta.threads.create()
    # Добавление сообщения от пользователя в нить
    response = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Рассчитай мою натальную карту и моего партнера."
                "Рассчитай нашу совместимость с партнером на основании этой информации "
                "Ты должен использовать как западный метод, так и Джойтиш."
                f"Моя дата рождения: {date}"
                f"Место моего рождения: {place}"
                f"Время моего рождения: {birth_time}"

                f" дата рождения партнера: {partner_date}"
                f"Место  рождения партнера: {partner_place}"
                f"Время  рождения партнера: {partner_birth_time}"

                f"Мы {type_relation}"

        # Текст сообщения от пользователя
    )
    content = (f"Рассчитай мою натальную карту и моего партнера."
               f"Рассчитай нашу совместимость с партнером на основании этой информации "
               f"Ты должен использовать как западный метод, так и Джойтиш."
               f"Моя дата рождения: {date} "
               f"Место моего рождения: {place} "
               f"Время моего рождения: {birth_time} "

               f" дата рождения партнера: {partner_date} "
               f"Место  рождения партнера: {partner_place} "
               f"Время  рождения партнера: {partner_birth_time} "

               f"Наш тип отношений {type_relation}")
    # Запуск ассистента для обработки сообщения
    run_response = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,  # Использование корректного ID ассистента
    )

    # Проверка статуса до завершения выполнения
    status = run_response.status
    while status != 'completed':
        run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread.id)
        status = run_status.status

        if status == 'failed':
            print("Запуск завершился с ошибкой")
            return

        if status == 'completed':
            break

        # Ожидание перед следующей проверкой статуса
        time.sleep(5)

    # Получение всех сообщений в нити
    messages_response = await client.beta.threads.messages.list(thread_id=thread.id)

    if messages_response.data:
        text = res(messages_response.data[0].content[0].text.value)
        return text
    else:
        print("Сообщений нет.")


async def generate_personality_compat(one_type, other_type, type_relation=None):
    # Проверка существования ассистента
    assistants_list = await client.beta.assistants.list()
    assistant = None

    for existing_assistant in assistants_list.data:
        if existing_assistant.name == "Lovele":
            assistant = existing_assistant
            break

    if assistant:
        print(f"Используется существующий ассистент с ID: {assistant.id}")
    else:
        print(f"Создан новый ассистент с ID: {assistant.id}")

    # Создание новой нити для диалога
    thread = await client.beta.threads.create()
    # Добавление сообщения от пользователя в нить
    response = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Мой тип личности {one_type}\n"
                f"Тип личности моего партнера{other_type}\n"
                f"Определи нашу совместимость, дай интересную и развернутую информацию\n"

                f"Мы {type_relation}"

        # Текст сообщения от пользователя
    )

    # Запуск ассистента для обработки сообщения
    run_response = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,  # Использование корректного ID ассистента
    )

    # Проверка статуса до завершения выполнения
    status = run_response.status
    while status != 'completed':
        run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread.id)
        status = run_status.status

        if status == 'failed':
            print("Запуск завершился с ошибкой")
            return

        if status == 'completed':
            break

        # Ожидание перед следующей проверкой статуса
        time.sleep(5)

    # Получение всех сообщений в нити
    messages_response = await client.beta.threads.messages.list(thread_id=thread.id)

    if messages_response.data:
        text = res(messages_response.data[0].content[0].text.value)
        return text
    else:
        print("Сообщений нет.")


async def generate_more_personality(personality, thread_id=None):
    assistant_id = await get_assistant()

    # Создаем новый тред, если он не был передан
    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id

    response = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"Мой тип личности {personality}\n"
                f"Что ты можешь сказать о нем? расскажи сильные стороны, слабые стороны, особенности характера."
                f"дай подробный и развернутый структурированный ответ",
    )

    max_retries = 5
    for attempt in range(max_retries):
        try:
            run_response = await client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )
            while True:
                run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread_id)
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logging.error("Запуск завершился с ошибкой")
                    return

                await asyncio.sleep(5)

            messages_response = await client.beta.threads.messages.list(thread_id=thread_id)
            if messages_response.data:
                text = res(messages_response.data[0].content[0].text.value)
                return text
            else:
                logging.info("Сообщений нет.")
                return None
        except openai.APIConnectionError as e:
            logging.warning(f"Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            if attempt == max_retries - 1:
                logging.error("Превышено максимальное количество попыток подключения.")
                raise e


async def generate_sisyphus_answer(user_id, personality, date, place, birth_time, sisyphus_theme, all_answers_text,
                                   max_retries=5):
    assistant_id = await get_assistant()
    thread_id = db.get_thread(user_id)

    content = f"""
Создай персонализированный 30-дневный план по теме "{sisyphus_theme}", с ежедневными задачами, адаптированными под мои особенности.

    **Инструкции по структуре плана:**
    1. Сократи вводное описание плана до одного короткого предложения. 
    2. Раздели план на 3 этапа и выдели заголовки этапов тегом <u>:
       - <u>Этап 1: Дни 1-10 — Формирование базовых навыков</u>
       - <u>Этап 2: Дни 11-20 — Углубление в практику</u>
       - <u>Этап 3: Дни 21-30 — Закрепление успехов</u>
    3. Каждый день начинай с тегов <b><u>День N</u></b>, чтобы выделить его название. Не пропускай и не сокращай дни — каждый день должен быть расписан индивидуально.

    **Требования к каждому дню:**
    - Подробно опиши задачи для каждого дня, с учётом моего типа личности, натальной карты и актуальных транзитов планет. **Не сокращай, например "Дни 1-3", каждый день должен быть расписан отдельно.**
    - Учитывай мой личный ритм, особенности и склонности.
    - В конце каждого этапа добавь небольшие упражнения для оценки прогресса и готовности к следующему этапу.

    **Мои данные для персонализации:**
    - Тип личности: {personality}
    - Дата рождения: {date}
    - Место рождения: {place}
    - Время рождения: {birth_time}
    - Ответы из интервью: {all_answers_text}

    **Формат ответа:** Подробный и структурированный план, разделённый по дням. Каждый день должен быть расписан индивидуально, без сокращений или объединений. Чётко структурированный план с выделением этапов тегом <u>, а каждый день — тегами <b><u>, с учётом астрологических влияний и особенностей моей личности.
    """

    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id

    response = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )

    for attempt in range(max_retries):
        try:
            run_response = await client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )
            while True:
                run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread_id)
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logging.error("Запуск завершился с ошибкой")
                    return

                await asyncio.sleep(5)

            messages_response = await client.beta.threads.messages.list(thread_id=thread_id)
            if messages_response.data:
                text = res(messages_response.data[0].content[0].text.value)
                return text
            else:
                logging.info("Сообщений нет.")
                return None
        except openai.APIConnectionError as e:
            logging.warning(f"Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            if attempt == max_retries - 1:
                logging.error("Превышено максимальное количество попыток подключения.")
                raise e


# async def generator(user_id, content, max_retries=15):
#     assistant_id = await get_assistant()
#     thread_id = db.get_thread(user_id)
#
#     if not thread_id:
#         thread = await client.beta.threads.create()
#         thread_id = thread.id
#
#     response = await client.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=content,
#     )
#
#     for attempt in range(max_retries):
#         try:
#             run_response = await client.beta.threads.runs.create(
#                 thread_id=thread_id,
#                 assistant_id=assistant_id,
#             )
#             while True:
#                 run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread_id)
#                 if run_status.status == 'completed':
#                     break
#                 elif run_status.status == 'failed':
#                     logging.error("Запуск завершился с ошибкой")
#
#                     return
#
#                 await asyncio.sleep(5)
#
#             messages_response = await client.beta.threads.messages.list(thread_id=thread_id)
#             if messages_response.data:
#                 text = res(messages_response.data[0].content[0].text.value)
#                 return text
#             else:
#                 logging.info("Сообщений нет.")
#                 return None
#         except openai.APIConnectionError as e:
#             logging.warning(f"Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
#             await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
#             if attempt == max_retries - 1:
#                 logging.error("Превышено максимальное количество попыток подключения.")
#                 raise e

async def generator(user_id, content, max_retries=15):

    # Получаем assistant_id
    try:
        assistant_id = await get_assistant()
    except Exception as e:
        logging.error(f"❌ Ошибка при получении assistant_id: {e}")
        return

    # Получаем thread_id из БД
    thread_id = db.get_thread(user_id)

    if not thread_id:
        # Если thread_id нет, создаем новый
        logging.info(f"📭 Поток не найден, создаю новый...")
        try:
            thread = await client.beta.threads.create()
            thread_id = thread.id
        except Exception as e:
            logging.error(f"❌ Ошибка при создании нового потока: {e}")
            return

    try:
        # Отправка сообщения пользователю
        response = await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке сообщения: {e}")
        return

    # Попытки запуска обработки
    for attempt in range(max_retries):
        try:
            logging.info(f"🚀 Создаю запуск для обработки (попытка {attempt + 1})...")
            run_response = await client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )

            while True:
                # Проверка статуса обработки
                run_status = await client.beta.threads.runs.retrieve(
                    run_id=run_response.id,
                    thread_id=thread_id
                )

                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logging.error("❌ Запуск завершился с ошибкой.")
                    return

                await asyncio.sleep(5)

            # Получение сообщений
            messages_response = await client.beta.threads.messages.list(thread_id=thread_id)

            if messages_response.data:
                # Обработка первого сообщения
                text = res(messages_response.data[0].content[0].text.value)
                return text
            else:
                logging.warning("⚠️ Сообщений нет.")
                return None

        except openai.APIConnectionError as e:
            logging.warning(f"🌐 Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            if attempt == max_retries - 1:
                logging.error("🚫 Превышено максимальное количество попыток подключения.")
                raise e

        except Exception as e:
            logging.error(f"❗ Неожиданная ошибка: {e}")
            raise e


async def generator_nothread(user_id, content, max_retries=10):
    assistant_id = await get_assistant()
    thread_id = db.get_thread(user_id)

    threadik = await client.beta.threads.create()
    threadik_id = threadik.id

    response = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )

    for attempt in range(max_retries):
        try:
            run_response = await client.beta.threads.runs.create(
                thread_id=threadik_id,
                assistant_id=assistant_id,
            )
            while True:
                run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=threadik_id)
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logging.error("Запуск завершился с ошибкой")

                    return

                await asyncio.sleep(5)

            messages_response = await client.beta.threads.messages.list(thread_id=threadik_id)
            if messages_response.data:
                text = res(messages_response.data[0].content[0].text.value)
                return text
            else:
                logging.info("Сообщений нет.")
                return None
        except openai.APIConnectionError as e:
            logging.warning(f"Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            if attempt == max_retries - 1:
                logging.error("Превышено максимальное количество попыток подключения.")
                raise e


async def generate_test(question, max_retries=5, thread_id=None):
    assistant_id = await get_assistant()

    content = f'{question}'

    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id

    response = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )

    for attempt in range(max_retries):
        try:
            run_response = await client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )
            while True:
                run_status = await client.beta.threads.runs.retrieve(run_id=run_response.id, thread_id=thread_id)
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logging.error("Запуск завершился с ошибкой")
                    return

                await asyncio.sleep(5)

            messages_response = await client.beta.threads.messages.list(thread_id=thread_id)
            if messages_response.data:
                text = res(messages_response.data[0].content[0].text.value)
                return text
            else:
                logging.info("Сообщений нет.")
                return None
        except openai.APIConnectionError as e:
            logging.warning(f"Ошибка подключения (попытка {attempt + 1} из {max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            if attempt == max_retries - 1:
                logging.error("Превышено максимальное количество попыток подключения.")
                raise e
