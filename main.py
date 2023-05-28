import asyncio
import logging

import openai
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import init_db
from handlers import router

from commands import add_commands


async def main():
    config = Config()
    openai.api_key = config.openai_token

    init_db()

    bot = Bot(token=config.telegram_token, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await add_commands(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
