import logging
import asyncio
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
# from aiohttp_socks import ProxyConnector
from aiogram.fsm.storage.memory import MemoryStorage

from config import TG_TOKEN
from app.handlers import router

from app.personality_type import router as personality_type_router
from app.personality_compat import router as personality_compat_router
from app.sisyphus import router as sisyphus_router
from app.todo_smart import router as todo_smart_router
from app.todo import router as todo_router
from app.todo_settings import router as todo_settings_router
from app.decomposer_to_todo import router as decomposer_to_todo_router
from app.energy_test import router as energy_test_router
from app.natal import router as natal_router
from app.life_test import router as life_test_router
from app.motivation_dream_five import router as motivation_dream_five_router
from scheduler import start_scheduler


async def main():
    # Настройка логгирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Логгер для записи в файл
    file_handler = RotatingFileHandler(
        "app.log", maxBytes=10**6, backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Добавляем обработчик ко всем логгерам
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    bot = Bot(token=TG_TOKEN)
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    dp.include_router(personality_type_router)
    dp.include_router(personality_compat_router)
    dp.include_router(sisyphus_router)
    dp.include_router(todo_smart_router)
    dp.include_router(todo_router)
    dp.include_router(todo_settings_router)
    dp.include_router(decomposer_to_todo_router)
    dp.include_router(energy_test_router)
    dp.include_router(natal_router)
    dp.include_router(life_test_router)
    dp.include_router(motivation_dream_five_router)

    start_scheduler(bot)


    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

