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


@router.message(Command("ask"))
async def start_dialog_handler(msg: aiogram.types.Message):
    text = msg.text.replace('/ask', '', 1).strip()

    if len(text) == 0:
        await msg.reply("Привет! Вы можете спросить бота о чем-нибудь. Просто используйте команду `/ask <вопрос>`")
        return

    chat_cache, _ = Chat.get_or_create(chat_id=msg.chat.id)
    msg_cache = Message.create(chat_id=msg.chat.id, message_id=msg.message_id, text=text)

    if chat_cache.is_dialog_now:
        await msg.reply("Теперь запущен диалоговый режим. Остановите диалог перед этим.", reply_markup=get_stop_dialog_keyboard())
        return
    else:
        new_msg = await msg.reply("Бот думает...")
        try:
            ans = await start_dialog(text)
        except RateLimitError:
            await msg.reply("Эта модель в настоящее время перегружена другими запросами. Вы можете повторить свой запрос.")
            return

        await new_msg.delete()
        ans_msg = await msg.reply(ans, reply_markup=get_continue_dialog_keyboard())
        msg_cache.answer = ans
        msg_cache.answer_id = ans_msg.message_id
        msg_cache.save()


@router.message()
async def on_message(msg: aiogram.types.Message):
    chat_cache, _ = Chat.get_or_create(chat_id=msg.chat.id)
    if not chat_cache.is_dialog_now:
        return

    text = msg.text
    if len(text) == 0 or text.startswith('//'):
        return

    new_msg = await msg.reply("Бот думает...")
    chat_cache = Chat.get(chat_id=msg.chat.id)

    DialogMessage.create(dialog=chat_cache.current_dialog, role='user', text=text)
    dialog_messages_cache = list(DialogMessage
                                 .select(DialogMessage.role, DialogMessage.text.alias('content'))
                                 .where(DialogMessage.dialog == chat_cache.current_dialog)
                                 .order_by(DialogMessage.id)
                                 .dicts()
                                 .execute())
    try:
        ans = await aiDriver.continue_dialog(dialog_messages_cache)
        DialogMessage.create(dialog=chat_cache.current_dialog, role='assistant', text=ans)
        await new_msg.delete()
        await msg.reply(ans, reply_markup=get_stop_dialog_keyboard())
    except RateLimitError:
        DialogMessage \
            .select() \
            .where(DialogMessage.dialog == chat_cache.current_dialog) \
            .order_by(DialogMessage.id) \
            .get() \
            .delete()
        await new_msg.delete()
        await msg.reply("Эта модель в настоящее время перегружена другими запросами. Вы можете повторить свой запрос.")
        return


@router.callback_query(lambda c: c.data.startswith('continue'))
async def continue_dialog(callback_query: CallbackQuery):
    chat_cache = Chat.get(chat_id=callback_query.message.chat.id)
    if chat_cache.is_dialog_now:
        await callback_query.message.reply('Диалоговый режим уже запущен. Остановите диалог перед этим.')
        await callback_query.message.edit_reply_markup(reply_markup=None)
        return

    dialog_cache = Dialog.create()
    DialogMessage.create(dialog=dialog_cache, role='system', text='You are a helpful assistant.')
    msg_cache = Message.get(answer_id=callback_query.message.message_id)
    DialogMessage.create(dialog=dialog_cache, role='user', text=msg_cache.text)
    DialogMessage.create(dialog=dialog_cache, role='assistant', text=msg_cache.answer)

    chat_cache.is_dialog_now = True
    chat_cache.current_dialog = dialog_cache
    chat_cache.save()

    await callback_query.message.reply('Диалог продолжался. Отправьте сообщение, чтобы задать какой-нибудь '
                                       'другой вопрос. Используйте префикс `//` чтобы бот игнорировал сообщения.',
                                       reply_markup=get_stop_dialog_keyboard())
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('stop'))
async def stop_dialog(callback_query: CallbackQuery):
    chat_cache = Chat.get(chat_id=callback_query.message.chat.id)
    if not chat_cache.is_dialog_now:
        await callback_query.message.reply('Диалоговый режим сейчас не запущен.')
        await callback_query.message.edit_reply_markup(reply_markup=None)
        return

    chat_cache.is_dialog_now = False
    chat_cache.save()

    await callback_query.message.reply('Диалог закончился. Используйте /ask, чтобы что-то спросить.')
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.answer()
