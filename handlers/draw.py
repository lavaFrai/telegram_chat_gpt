import aiogram
import openai
from aiogram import types, F, Router
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from openai.error import RateLimitError

import aiDriver
from database import Message, Chat, Dialog, DialogMessage
from aiDriver import start_dialog
from keyboard import get_continue_dialog_keyboard, get_stop_dialog_keyboard

router = Router()


@router.message()
async def draw_handler(msg: aiogram.types.Message):
    text = msg.text.replace('/draw', '', 1).strip()

    if len(text) == 0:
        await msg.reply("Привет! Вы можете попросить бота нарисовать что либо. Просто используйте команду `/draw <тема>`")
        return

    new_msg = await msg.reply("Уже рисуем...")

    try:
        response = await openai.Image.acreate(
            prompt=text,
            n=1,
            size='512x512'
        )
        image_url = response['data'][0]['url']
    except openai.error.InvalidRequestError:
        await new_msg.delete()
        await msg.reply("Кажется, ваш запрос был неприемлем, мы не смогли создать картинку")
        return

    await new_msg.delete()
    await msg.reply_photo(photo=image_url)
