import aiogram
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


@router.message(Command("start"))
async def start_handler(msg: aiogram.types.Message):
    await msg.answer("Привет! Добро пожаловать в чат-бот с искусственным интеллектом. Вы можете спросить что-нибудь, "
                     "используя команду /ask.")
