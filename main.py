import asyncio
import logging
import os.path
import uuid

import openai
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Voice
from pydub import AudioSegment

from config import Config
from database import init_db

from commands import add_commands

handlers = [
    'handlers.ping',
    'handlers.start',
    'handlers.draw',
    'handlers.chat_dialog',
]

config = Config()
openai.api_key = config.openai_token
bot = Bot(token=config.telegram_token, parse_mode=ParseMode.MARKDOWN)


async def download_file(file_id):
    if not os.path.exists("downloads"):
        os.mkdir("downloads")

    unique_filename = str(uuid.uuid4())
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, "downloads/" + unique_filename)
    return "downloads/" + unique_filename


async def set_file_extension(file, extension):
    os.rename(file, file + '.' + extension)
    return file + '.' + extension


async def remove_file(file):
    os.remove(file)


async def download_voice_mp3(voice: Voice):
    file = await download_file(voice.file_id)
    AudioSegment.from_ogg(file).export(file + '.mp3', format="mp3")
    await remove_file(file)
    return file + '.mp3'


async def main():
    init_db()

    dp = Dispatcher(storage=MemoryStorage())
    for module in handlers:
        dp.include_router(__import__(module, fromlist=['router']).router)

    await add_commands(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
