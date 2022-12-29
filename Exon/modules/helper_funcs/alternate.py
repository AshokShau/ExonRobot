from functools import wraps

from telegram import Message, Update
from telegram.constants import ChatAction
from telegram.error import BadRequest
from telegram.ext import ContextTypes


async def send_message(message: Message, text, *args, **kwargs):
    try:
        return await message.reply_text(text, *args, **kwargs)
    except BadRequest as err:
        if str(err) == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            return await message.reply_text(text, quote=False, *args, **kwargs)


def typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )
        return await func(update, context, *args, **kwargs)

    return command_func


def sticker_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.CHOOSE_STICKER,
        )
        return await func(update, context, *args, **kwargs)

    return command_func


def document_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_DOCUMENT,
        )
        return await func(update, context, *args, **kwargs)

    return command_func


def photo_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_PHOTO,
        )
        return await func(update, context, *args, **kwargs)

    return command_func
